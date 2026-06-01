"""TTS service — supports ElevenLabs/Volcano API and CosyVoice (GPU server)."""
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def synthesize(
    text: str,
    voice_id: str = "default",
    speed: float = 1.0,
    provider: str = "elevenlabs",
) -> bytes:
    """Synthesize speech from text.

    GPU mode: CosyVoice on GPU server.
    API mode: ElevenLabs or Volcano Engine (based on provider param).
    """
    if settings.AI_BACKEND == "gpu":
        return _synthesize_cosyvoice(text, voice_id, speed)

    if provider == "volcano":
        return synthesize_volcano(text, voice_id)
    return synthesize_elevenlabs(text, voice_id, speed=speed)


# ---------------------------------------------------------------------------
# GPU mode: CosyVoice
# ---------------------------------------------------------------------------

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def _synthesize_cosyvoice(text: str, voice_id: str = "default", speed: float = 1.0) -> bytes:
    """Synthesize speech via CosyVoice API on GPU server."""
    base = settings.COSYVOICE_BASE_URL.rstrip("/")
    resp = httpx.post(
        f"{base}/tts",
        json={
            "text": text,
            "voice": voice_id,
            "speed": speed,
        },
        timeout=120,
    )
    resp.raise_for_status()
    data = resp.json()
    audio_url = data.get("audio_url", "")
    if audio_url:
        audio_resp = httpx.get(audio_url if audio_url.startswith("http") else f"{base}{audio_url}", timeout=60)
        audio_resp.raise_for_status()
        return audio_resp.content
    raise RuntimeError("CosyVoice returned no audio")


# ---------------------------------------------------------------------------
# API mode: ElevenLabs
# ---------------------------------------------------------------------------

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def synthesize_elevenlabs(
    text: str,
    voice_id: str,
    stability: float = 0.5,
    similarity_boost: float = 0.75,
    style: float = 0.0,
    speed: float = 1.0,
) -> bytes:
    """Synthesize speech using ElevenLabs API."""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": settings.ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": stability, "similarity_boost": similarity_boost, "style": style, "speed": speed},
    }
    resp = httpx.post(url, json=payload, headers=headers, timeout=60)
    resp.raise_for_status()
    return resp.content


# ---------------------------------------------------------------------------
# API mode: Volcano Engine
# ---------------------------------------------------------------------------

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def synthesize_volcano(text: str, voice_type: str = "zh_female_xiaomei_moon_bigtts") -> bytes:
    """Synthesize speech using Volcano Engine TTS."""
    import base64
    headers = {
        "Authorization": f"Bearer;{settings.VOLC_TTS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "app": {"appid": settings.VOLC_TTS_APP_ID, "token": settings.VOLC_TTS_TOKEN, "cluster": "volcano_tts"},
        "user": {"uid": "musegen"},
        "audio": {"voice_type": voice_type, "encoding": "mp3", "rate": 24000},
        "request": {"reqid": "1", "text": text, "text_type": "plain", "operation": "query"},
    }
    resp = httpx.post("https://openspeech.bytedance.com/api/v1/tts", json=payload, headers=headers, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    audio_b64 = data.get("data", {}).get("audio", "")
    return base64.b64decode(audio_b64)