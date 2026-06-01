"""TTS service — ElevenLabs and Volcano Engine."""
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings

ELEVENLABS_TTS_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def synthesize_elevenlabs(
    text: str,
    voice_id: str,
    stability: float = 0.5,
    similarity_boost: float = 0.75,
    style: float = 0.0,
    speed: float = 1.0,
) -> bytes:
    """Synthesize speech using ElevenLabs API.

    Args:
        text: Text to synthesize.
        voice_id: ElevenLabs voice ID.
        stability: Voice stability (0-1).
        similarity_boost: Voice similarity boost (0-1).
        style: Style exaggeration (0-1).
        speed: Speaking speed multiplier.

    Returns:
        Raw MP3 audio bytes.
    """
    url = ELEVENLABS_TTS_URL.format(voice_id=voice_id)
    headers = {
        "xi-api-key": settings.ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": stability,
            "similarity_boost": similarity_boost,
            "style": style,
            "speed": speed,
        },
    }

    response = httpx.post(url, json=payload, headers=headers, timeout=60)
    response.raise_for_status()
    return response.content


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def synthesize_volcano(text: str, voice_type: str = "zh_female_xiaomei_moon_bigtts") -> bytes:
    """Synthesize speech using Volcano Engine TTS.

    Args:
        text: Text to synthesize.
        voice_type: Volcano voice type code.

    Returns:
        Raw audio bytes.
    """
    url = "https://openspeech.bytedance.com/api/v1/tts"
    headers = {
        "Authorization": f"Bearer;{settings.VOLC_TTS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "app": {
            "appid": settings.VOLC_TTS_APP_ID,
            "token": settings.VOLC_TTS_TOKEN,
            "cluster": "volcano_tts",
        },
        "user": {"uid": "musegen"},
        "audio": {
            "voice_type": voice_type,
            "encoding": "mp3",
            "rate": 24000,
        },
        "request": {
            "reqid": "1",
            "text": text,
            "text_type": "plain",
            "operation": "query",
        },
    }

    response = httpx.post(url, json=payload, headers=headers, timeout=60)
    response.raise_for_status()
    data = response.json()
    import base64
    audio_b64 = data.get("data", {}).get("audio", "")
    return base64.b64decode(audio_b64)
