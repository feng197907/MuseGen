"""Video generation service via Replicate SVD (Stable Video Diffusion)."""
import replicate
import httpx
import os
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings

os.environ.setdefault("REPLICATE_API_TOKEN", settings.REPLICATE_API_TOKEN)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=30))
def generate_video_from_image(
    image_url: str,
    num_frames: int = 25,
    fps: int = 6,
    motion_bucket_id: int = 127,
    cond_aug: float = 0.02,
) -> bytes:
    """Generate a short video clip from a keyframe image using SVD.

    Args:
        image_url: URL of the starting keyframe image.
        num_frames: Total number of frames to generate.
        fps: Frames per second.
        motion_bucket_id: Motion amount (higher = more motion).
        cond_aug: Conditioning augmentation level.

    Returns:
        Raw video bytes (MP4).
    """
    output = replicate.run(
        settings.SVD_MODEL_VERSION,
        input={
            "input_image": image_url,
            "num_frames": num_frames,
            "fps": fps,
            "motion_bucket_id": motion_bucket_id,
            "cond_aug": cond_aug,
            "decoding_t": 7,
            "video_length": "14_frames_with_svd",
        },
    )

    # SVD output is a video URL
    video_url = output
    response = httpx.get(str(video_url), timeout=120)
    response.raise_for_status()
    return response.content
