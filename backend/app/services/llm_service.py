"""LLM service — supports OpenAI API and local Ollama (GPU server)."""
import json
from typing import Any
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings
from app.utils.prompt_templates import STORY_PARSE_PROMPT


def _get_client() -> OpenAI:
    """Return OpenAI-compatible client based on AI_BACKEND setting."""
    if settings.AI_BACKEND == "gpu":
        return OpenAI(
            base_url=settings.OLLAMA_BASE_URL,
            api_key="ollama",
        )
    else:
        return OpenAI(api_key=settings.OPENAI_API_KEY)


def _get_model() -> str:
    """Return model name based on AI_BACKEND setting."""
    if settings.AI_BACKEND == "gpu":
        return settings.OLLAMA_MODEL
    return settings.OPENAI_MODEL


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def parse_story(story_text: str) -> dict[str, Any]:
    """Send story text to LLM and get back structured characters/scenes/shots."""
    client = _get_client()
    model = _get_model()

    response = client.chat.completions.create(
        model=model,
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
    """Generate an SDXL prompt for a single shot."""
    client = _get_client()
    model = _get_model()

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
        model=model,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.8,
        max_tokens=256,
    )
    return response.choices[0].message.content.strip()