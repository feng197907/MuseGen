"""LLM service — OpenAI GPT-4o for story parsing and prompt generation."""
import json
from typing import Any
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings
from app.utils.prompt_templates import STORY_PARSE_PROMPT

client = OpenAI(api_key=settings.OPENAI_API_KEY)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def parse_story(story_text: str) -> dict[str, Any]:
    """Send story text to GPT-4o and get back structured characters/scenes/shots.

    Args:
        story_text: Raw story text from user.

    Returns:
        Dict with keys: characters, scenes, shots
    """
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": STORY_PARSE_PROMPT},
            {"role": "user", "content": f"请解析以下故事文本：\n\n{story_text}"},
        ],
        temperature=0.7,
        max_tokens=4096,
    )
    return json.loads(response.choices[0].message.content)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def generate_shot_prompt(
    shot_description: str,
    character_descriptions: list[str],
    scene_description: str,
    shot_type: str,
    mood: str,
) -> str:
    """Generate an SDXL prompt for a single shot.

    Args:
        shot_description: Text description of the shot content.
        character_descriptions: List of character appearance strings.
        scene_description: Scene setting description.
        shot_type: Camera shot type (中景, 特写, etc.).
        mood: Emotional tone of the shot.

    Returns:
        Optimized prompt string for SDXL generation.
    """
    system_msg = (
        "You are an expert anime prompt engineer. "
        "Generate a concise, high-quality SDXL prompt in English for anime image generation. "
        "Output only the prompt, no explanation."
    )

    user_msg = (
        f"Shot type: {shot_type}\n"
        f"Mood: {mood}\n"
        f"Scene: {scene_description}\n"
        f"Characters: {', '.join(character_descriptions)}\n"
        f"Shot content: {shot_description}\n"
        "Generate the SDXL prompt:"
    )

    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.8,
        max_tokens=256,
    )
    return response.choices[0].message.content.strip()
