"""Image generation service via Replicate SDXL."""
import replicate
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings

# Initialize Replicate client (uses REPLICATE_API_TOKEN env var)
import os
os.environ.setdefault("REPLICATE_API_TOKEN", settings.REPLICATE_API_TOKEN)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=30))
def generate_image(
    prompt: str,
    negative_prompt: str = "",
    width: int = 1024,
    height: int = 576,
    num_inference_steps: int = 30,
    guidance_scale: float = 7.5,
) -> bytes:
    """Generate an image using SDXL via Replicate.

    Args:
        prompt: Positive prompt for image generation.
        negative_prompt: Negative prompt to exclude unwanted elements.
        width: Output image width in pixels.
        height: Output image height in pixels.
        num_inference_steps: Number of denoising steps.
        guidance_scale: Classifier-free guidance scale.

    Returns:
        Raw image bytes (PNG).
    """
    output = replicate.run(
        settings.SDXL_MODEL_VERSION,
        input={
            "prompt": prompt,
            "negative_prompt": negative_prompt or "low quality, blurry, bad anatomy, watermark",
            "width": width,
            "height": height,
            "num_inference_steps": num_inference_steps,
            "guidance_scale": guidance_scale,
            "scheduler": "K_EULER",
            "num_outputs": 1,
        },
    )

    image_url = output[0]
    response = httpx.get(str(image_url), timeout=60)
    response.raise_for_status()
    return response.content


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=30))
def generate_image_with_reference(
    prompt: str,
    reference_image_url: str,
    negative_prompt: str = "",
    ip_adapter_scale: float = 0.6,
    width: int = 1024,
    height: int = 576,
) -> bytes:
    """Generate image using SDXL + IP-Adapter for character consistency.

    Args:
        prompt: Positive prompt.
        reference_image_url: URL of reference image (character portrait).
        negative_prompt: Negative prompt.
        ip_adapter_scale: Strength of IP-Adapter reference (0-1).
        width: Output width.
        height: Output height.

    Returns:
        Raw image bytes (PNG).
    """
    output = replicate.run(
        settings.SDXL_MODEL_VERSION,
        input={
            "prompt": prompt,
            "negative_prompt": negative_prompt or "low quality, blurry, bad anatomy",
            "ip_adapter_image": reference_image_url,
            "ip_adapter_scale": ip_adapter_scale,
            "width": width,
            "height": height,
            "num_inference_steps": 30,
            "guidance_scale": 7.5,
        },
    )

    image_url = output[0]
    response = httpx.get(str(image_url), timeout=60)
    response.raise_for_status()
    return response.content
