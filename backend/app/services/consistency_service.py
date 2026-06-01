"""Character consistency service using IP-Adapter parameter encapsulation."""
from typing import Optional
from app.services.image_service import generate_image_with_reference


def build_consistency_params(
    character_image_url: str,
    ip_adapter_scale: float = 0.6,
    controlnet_scale: float = 0.5,
) -> dict:
    """Build IP-Adapter + ControlNet parameters for character-consistent generation.

    Args:
        character_image_url: URL of the character reference image.
        ip_adapter_scale: Weight of IP-Adapter reference (0-1).
        controlnet_scale: Weight of ControlNet conditioning (0-1).

    Returns:
        Dict of parameters to merge into the image generation payload.
    """
    return {
        "ip_adapter_image": character_image_url,
        "ip_adapter_scale": ip_adapter_scale,
        "controlnet_conditioning_scale": controlnet_scale,
    }


def generate_consistent_keyframe(
    prompt: str,
    character_image_url: str,
    negative_prompt: str = "",
    ip_adapter_scale: float = 0.6,
    width: int = 1024,
    height: int = 576,
) -> bytes:
    """Generate a keyframe with character consistency via IP-Adapter.

    Args:
        prompt: Shot prompt.
        character_image_url: Character reference image URL.
        negative_prompt: Negative prompt.
        ip_adapter_scale: Consistency strength.
        width: Output width.
        height: Output height.

    Returns:
        Raw image bytes.
    """
    return generate_image_with_reference(
        prompt=prompt,
        reference_image_url=character_image_url,
        negative_prompt=negative_prompt,
        ip_adapter_scale=ip_adapter_scale,
        width=width,
        height=height,
    )
