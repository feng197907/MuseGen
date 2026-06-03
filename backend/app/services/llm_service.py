"""LLM service — supports OpenAI API and local Ollama (GPU server)."""
import json
import re
import logging
from typing import Any
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings
from app.utils.prompt_templates import STORY_PARSE_PROMPT

logger = logging.getLogger(__name__)


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


def _fix_json_syntax(text: str) -> str:
    """Attempt to fix common JSON syntax errors from LLM output."""
    # Remove trailing commas before closing brackets/braces
    text = re.sub(r',\s*}', '}', text)
    text = re.sub(r',\s*]', ']', text)
    # Fix single quotes to double quotes (but not within quoted strings)
    # Simple approach: replace 'key': with "key":
    text = re.sub(r"'([^']*)'\s*:", r'"\1":', text)
    text = re.sub(r":\s*'([^']*)'", r': "\1"', text)
    return text


def _extract_json(text: str) -> dict[str, Any]:
    """Extract JSON from LLM response, handling markdown fences and extra text."""
    if not text or not text.strip():
        raise ValueError("LLM returned empty response")

    original_text = text

    # Try direct parse first
    candidates: list[str] = [text]

    # Try to extract from ```json ... ``` code fence
    fence_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
    if fence_match:
        candidates.append(fence_match.group(1))

    # Try to find outermost { ... }
    brace_match = re.search(r'\{.*\}', text, re.DOTALL)
    if brace_match:
        candidates.append(brace_match.group(0))

    # Try multiple brace pairs in case of nested objects (find matching braces)
    remaining = text
    for _ in range(5):
        start = remaining.find('{')
        if start == -1:
            break
        depth = 0
        for i in range(start, len(remaining)):
            if remaining[i] == '{':
                depth += 1
            elif remaining[i] == '}':
                depth -= 1
                if depth == 0:
                    candidates.append(remaining[start:i + 1])
                    remaining = remaining[i + 1:]
                    break

    last_err = None
    # Try each candidate with and without syntax fixes
    for i, candidate in enumerate(candidates):
        candidate = candidate.strip()
        if not candidate:
            continue
        # Try raw
        try:
            result = json.loads(candidate)
            logger.info(f"JSON parsed successfully from candidate #{i}")
            return result
        except json.JSONDecodeError:
            pass
        # Try with syntax fixes
        try:
            fixed = _fix_json_syntax(candidate)
            result = json.loads(fixed)
            logger.info(f"JSON parsed after syntax fix from candidate #{i}")
            return result
        except json.JSONDecodeError as e:
            last_err = e

    raise ValueError(
        f"Unable to extract valid JSON from LLM response. "
        f"First 800 chars: {original_text[:800]}... "
        f"Last parse error: {last_err}"
    )


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def parse_story(story_text: str) -> dict[str, Any]:
    """Send story text to LLM and get back structured characters/scenes/shots."""
    client = _get_client()
    model = _get_model()

    # Truncate story if too long (to avoid JSON truncation in response)
    max_story_len = 3000
    if len(story_text) > max_story_len:
        story_text = story_text[:max_story_len]
        logger.warning(f"Story truncated from original length to {max_story_len} chars")

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": STORY_PARSE_PROMPT},
            {"role": "user", "content": f"请解析以下故事文本，输出纯JSON（不要markdown代码块）：\n\n{story_text}"},
        ],
        temperature=0.3,
        max_tokens=4096,
    )
    content = response.choices[0].message.content
    logger.info(f"LLM response length: {len(content) if content else 0}")
    return _extract_json(content or "")


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
        "ALL prompts MUST include this exact style phrase: "
        "'modern anime, cel shading, crisp clean lineart, vibrant colors, studio quality' "
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