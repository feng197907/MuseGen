"""Image generation service — supports Replicate API and ComfyUI (GPU server)."""
import time
import uuid
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings
from app.utils.prompt_templates import NEGATIVE_PROMPT_DEFAULT, ANIME_STYLE_PREFIX

# ---------------------------------------------------------------------------
# ComfyUI helpers
# ---------------------------------------------------------------------------

COMFYUI_SD_WORKFLOW = {
    "3": {"class_type": "KSampler", "inputs": {"seed": 0, "steps": 30, "cfg": 8.0, "sampler_name": "dpmpp_2m", "scheduler": "karras", "denoise": 1.0, "model": ["4", 0], "positive": ["6", 0], "negative": ["7", 0], "latent_image": ["5", 0]}},
    "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "v1-5-pruned-emaonly-fp16.safetensors"}},
    "5": {"class_type": "EmptyLatentImage", "inputs": {"width": 512, "height": 512, "batch_size": 1}},
    "6": {"class_type": "CLIPTextEncode", "inputs": {"text": "PLACEHOLDER_POSITIVE", "clip": ["4", 1]}},
    "7": {"class_type": "CLIPTextEncode", "inputs": {"text": "PLACEHOLDER_NEGATIVE", "clip": ["4", 1]}},
    "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
    "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": "musegen", "images": ["8", 0]}},
}


def _build_comfyui_workflow(prompt: str, negative_prompt: str, width: int, height: int) -> dict:
    """Build a ComfyUI workflow dict for SD 1.5 generation."""
    import copy
    wf = copy.deepcopy(COMFYUI_SD_WORKFLOW)
    wf["3"]["inputs"]["seed"] = int(time.time() * 1000) % (2**32)
    wf["5"]["inputs"]["width"] = width
    wf["5"]["inputs"]["height"] = height
    wf["6"]["inputs"]["text"] = ANIME_STYLE_PREFIX + prompt
    wf["7"]["inputs"]["text"] = negative_prompt or NEGATIVE_PROMPT_DEFAULT
    return wf


def _comfyui_generate(workflow: dict) -> bytes:
    """Submit workflow to ComfyUI, poll until done, download result image."""
    import logging
    logger = logging.getLogger(__name__)
    base = settings.COMFYUI_BASE_URL.rstrip("/")

    resp = httpx.post(f"{base}/prompt", json={
        "prompt": workflow,
        "client_id": str(uuid.uuid4()),
        "extra_data": {"extra_pnginfo": {}},
    }, timeout=30)
    if not resp.is_success:
        logger.error(f"ComfyUI /prompt returned {resp.status_code}: {resp.text[:1000]}")
    resp.raise_for_status()
    prompt_id = resp.json()["prompt_id"]

    for _ in range(120):
        time.sleep(2)
        history_resp = httpx.get(f"{base}/history/{prompt_id}", timeout=10)
        history_resp.raise_for_status()
        history = history_resp.json()
        if prompt_id in history:
            for node_id, node_output in history[prompt_id]["outputs"].items():
                images = node_output.get("images", [])
                if images:
                    params = {"filename": images[0]["filename"], "type": images[0].get("type", "output")}
                    if images[0].get("subfolder"):
                        params["subfolder"] = images[0]["subfolder"]
                    img_resp = httpx.get(f"{base}/view", params=params, timeout=30)
                    img_resp.raise_for_status()
                    return img_resp.content
    raise TimeoutError(f"ComfyUI generation timed out for prompt_id={prompt_id}")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_image(
    prompt: str,
    negative_prompt: str = "",
    width: int = 1024,
    height: int = 576,
    num_inference_steps: int = 30,
    guidance_scale: float = 7.5,
) -> bytes:
    """Generate an anime-style image. GPU mode: ComfyUI. API mode: Replicate."""
    if settings.AI_BACKEND == "gpu":
        return _comfyui_generate(_build_comfyui_workflow(prompt, negative_prompt, width, height))

    # ── API mode: Replicate ──
    import os
    import replicate
    os.environ.setdefault("REPLICATE_API_TOKEN", settings.REPLICATE_API_TOKEN)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=30))
    def _run():
        output = replicate.run(settings.SDXL_MODEL_VERSION, input={
            "prompt": ANIME_STYLE_PREFIX + prompt,
            "negative_prompt": negative_prompt or NEGATIVE_PROMPT_DEFAULT,
            "width": width, "height": height,
            "num_inference_steps": num_inference_steps, "guidance_scale": guidance_scale,
            "scheduler": "K_EULER", "num_outputs": 1,
        })
        url = output[0] if isinstance(output, list) else output
        r = httpx.get(str(url), timeout=60)
        r.raise_for_status()
        return r.content
    return _run()


def generate_image_with_reference(
    prompt: str,
    reference_image_url: str,
    negative_prompt: str = "",
    ip_adapter_scale: float = 0.6,
    width: int = 1024,
    height: int = 576,
) -> bytes:
    """Generate image with character consistency via IP-Adapter."""
    if settings.AI_BACKEND == "gpu":
        return _comfyui_ipadapter(prompt, reference_image_url, negative_prompt, ip_adapter_scale, width, height)

    import os
    import replicate
    os.environ.setdefault("REPLICATE_API_TOKEN", settings.REPLICATE_API_TOKEN)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=30))
    def _run():
        output = replicate.run(settings.SDXL_MODEL_VERSION, input={
            "prompt": ANIME_STYLE_PREFIX + prompt,
            "negative_prompt": negative_prompt or NEGATIVE_PROMPT_DEFAULT,
            "ip_adapter_image": reference_image_url, "ip_adapter_scale": ip_adapter_scale,
            "width": width, "height": height,
            "num_inference_steps": 30, "guidance_scale": 7.5,
        })
        url = output[0] if isinstance(output, list) else output
        r = httpx.get(str(url), timeout=60)
        r.raise_for_status()
        return r.content
    return _run()


def _comfyui_ipadapter(
    prompt: str, reference_url: str, negative_prompt: str,
    ip_adapter_scale: float, width: int, height: int,
) -> bytes:
    """Generate via ComfyUI with IP-Adapter for character consistency."""
    import copy
    base = settings.COMFYUI_BASE_URL.rstrip("/")

    # Download and upload reference image to ComfyUI
    ref_bytes = httpx.get(reference_url, timeout=60).content
    upload_resp = httpx.post(f"{base}/upload/image", files={"image": ("ref.png", ref_bytes, "image/png")}, timeout=30)
    upload_resp.raise_for_status()
    ref_name = upload_resp.json()["name"]

    wf = copy.deepcopy(COMFYUI_SD_WORKFLOW)
    wf["10"] = {"class_type": "IPAdapter", "inputs": {"image": ref_name, "weight": ip_adapter_scale, "model": ["4", 0], "clip_vision": ["4", 0]}}
    wf["3"]["inputs"]["model"] = ["10", 0]
    wf["3"]["inputs"]["seed"] = int(time.time() * 1000) % (2**32)
    wf["5"]["inputs"]["width"] = width
    wf["5"]["inputs"]["height"] = height
    wf["6"]["inputs"]["text"] = ANIME_STYLE_PREFIX + prompt
    wf["7"]["inputs"]["text"] = negative_prompt or NEGATIVE_PROMPT_DEFAULT
    return _comfyui_generate(wf)