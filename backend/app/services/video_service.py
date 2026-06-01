"""Video generation service — supports Replicate SVD and ComfyUI AnimateDiff (GPU server)."""
import time
import uuid
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings


# ---------------------------------------------------------------------------
# ComfyUI AnimateDiff helpers
# ---------------------------------------------------------------------------

def _comfyui_generate_video(image_url: str, num_frames: int = 25, fps: int = 6) -> bytes:
    """Generate a short video clip via ComfyUI with AnimateDiff workflow.

    Downloads the input keyframe from S3, uploads to ComfyUI, runs AnimateDiff.
    """
    base = settings.COMFYUI_BASE_URL.rstrip("/")

    # Download keyframe image
    img_bytes = httpx.get(image_url, timeout=60).content

    # Upload to ComfyUI
    upload_resp = httpx.post(
        f"{base}/upload/image",
        files={"image": ("keyframe.png", img_bytes, "image/png")},
        timeout=30,
    )
    upload_resp.raise_for_status()
    img_name = upload_resp.json()["name"]

    # Minimal AnimateDiff workflow
    workflow = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "dreamshaperXL_v21TurboDPMSDE.safetensors"}},
        "2": {"class_type": "LoadImage", "inputs": {"image": img_name}},
        "3": {"class_type": "VAEEncode", "inputs": {"pixels": ["2", 0], "vae": ["1", 2]}},
        "4": {"class_type": "AnimateDiffLoaderV1", "inputs": {"model": ["1", 0], "latents": ["3", 0], "motion_module": "mm_sd_v15_v2.ckpt", "motion_scale": 1.0, "apply_motion_model": "enable"}},
        "5": {"class_type": "KSampler", "inputs": {"seed": int(time.time() * 1000) % (2**32), "steps": 25, "cfg": 7.5, "sampler_name": "euler", "scheduler": "normal", "denoise": 0.7, "model": ["4", 0], "positive": ["6", 0], "negative": ["7", 0], "latent_image": ["3", 0]}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": "smooth motion, high quality animation", "clip": ["1", 1]}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"text": "blurry, distorted, bad quality", "clip": ["1", 1]}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
        "9": {"class_type": "VHS_VideoCombine", "inputs": {"images": ["8", 0], "frame_rate": fps, "format": "video/h264-mp4", "filename_prefix": "musegen_vid"}},
    }

    resp = httpx.post(f"{base}/prompt", json={"prompt": workflow, "client_id": str(uuid.uuid4())}, timeout=30)
    resp.raise_for_status()
    prompt_id = resp.json()["prompt_id"]

    for _ in range(180):
        time.sleep(3)
        history_resp = httpx.get(f"{base}/history/{prompt_id}", timeout=10)
        history_resp.raise_for_status()
        history = history_resp.json()
        if prompt_id in history:
            for node_id, node_output in history[prompt_id]["outputs"].items():
                gifs = node_output.get("gifs", [])
                if gifs:
                    params = {"filename": gifs[0]["filename"], "type": gifs[0].get("type", "output")}
                    if gifs[0].get("subfolder"):
                        params["subfolder"] = gifs[0]["subfolder"]
                    vid_resp = httpx.get(f"{base}/view", params=params, timeout=60)
                    vid_resp.raise_for_status()
                    return vid_resp.content
    raise TimeoutError(f"ComfyUI video generation timed out for prompt_id={prompt_id}")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_video_from_image(
    image_url: str,
    num_frames: int = 25,
    fps: int = 6,
    motion_bucket_id: int = 127,
    cond_aug: float = 0.02,
) -> bytes:
    """Generate a short video clip from a keyframe image.

    GPU mode: ComfyUI AnimateDiff.
    API mode: Replicate SVD.
    """
    if settings.AI_BACKEND == "gpu":
        return _comfyui_generate_video(image_url, num_frames, fps)

    # ── API mode: Replicate SVD ──
    import os
    import replicate
    os.environ.setdefault("REPLICATE_API_TOKEN", settings.REPLICATE_API_TOKEN)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=30))
    def _run():
        output = replicate.run(settings.SVD_MODEL_VERSION, input={
            "input_image": image_url, "num_frames": num_frames, "fps": fps,
            "motion_bucket_id": motion_bucket_id, "cond_aug": cond_aug,
            "decoding_t": 7, "video_length": "14_frames_with_svd",
        })
        url = output
        r = httpx.get(str(url), timeout=120)
        r.raise_for_status()
        return r.content
    return _run()