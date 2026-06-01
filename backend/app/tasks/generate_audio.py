"""Celery Task: Generate audio/dubbing for each shot using TTS."""
import asyncio
from app.tasks.celery_app import celery_app
from app.services.tts_service import synthesize_elevenlabs, synthesize_volcano
from app.core.storage import upload_bytes
from app.utils.progress import update_progress
from app.core.database import async_session_factory
from app.models.storyboard import Shot
from app.models.asset import Character
from app.models.audio import AudioTrack, AudioType, VoiceProfile
from sqlalchemy import select
from sqlalchemy.orm import selectinload


@celery_app.task(bind=True, max_retries=2, default_retry_delay=30)
def run_generate_audio(
    self, task_id: str, project_id: str, shot_ids: list = None, chain_result=None
):
    """Generate TTS audio for all shots with dialogue."""
    if chain_result and isinstance(chain_result, dict):
        project_id = chain_result.get("project_id", project_id)

    update_progress(task_id, "generate_audio", "running", 10, "Starting TTS generation...")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(_generate_audio_tracks(task_id, project_id, shot_ids or []))

    update_progress(task_id, "generate_audio", "done", 100, "Audio tracks generated")
    return {"project_id": project_id, "task_id": task_id}


async def _generate_audio_tracks(task_id: str, project_id: str, shot_ids: list):
    """TTS for each shot that has dialogue."""
    async with async_session_factory() as session:
        from app.models.storyboard import Storyboard
        stmt = (
            select(Storyboard)
            .where(Storyboard.project_id == project_id)
            .options(selectinload(Storyboard.shots))
        )
        result = await session.execute(stmt)
        storyboard = result.scalar_one_or_none()
        if not storyboard:
            return
        shots = [s for s in storyboard.shots if s.dialogue.strip()]
        if shot_ids:
            shots = [s for s in shots if s.id in shot_ids]

    total = max(len(shots), 1)
    for idx, shot in enumerate(shots):
        if not shot.dialogue.strip():
            continue

        update_progress(
            task_id, "generate_audio", "running",
            10 + int(80 * idx / total),
            f"TTS synthesis {idx + 1}/{total}: {shot.title}",
        )

        try:
            # Look up voice profile for the first character in this shot
            voice_id = "21m00Tcm4TlvDq8ikWAM"  # Default ElevenLabs voice
            provider = "elevenlabs"
            voice_settings = {}

            if shot.character_ids:
                async with async_session_factory() as session:
                    char_stmt = select(Character).where(
                        Character.id == shot.character_ids[0]
                    ).options(selectinload(Character.voice_profile))
                    char_result = await session.execute(char_stmt)
                    char = char_result.scalar_one_or_none()
                    if char and char.voice_profile:
                        voice_id = char.voice_profile.voice_id
                        provider = char.voice_profile.provider
                        voice_settings = char.voice_profile.settings or {}

            # Synthesize
            if provider == "volcano":
                audio_bytes = synthesize_volcano(shot.dialogue)
            else:
                audio_bytes = synthesize_elevenlabs(
                    text=shot.dialogue,
                    voice_id=voice_id,
                    stability=voice_settings.get("stability", 0.5),
                    similarity_boost=voice_settings.get("similarityBoost", 0.75),
                    style=voice_settings.get("style", 0.0),
                    speed=voice_settings.get("speed", 1.0),
                )

            url = upload_bytes(audio_bytes, project_id, "audio", "mp3", "audio/mpeg")

            # Calculate start time based on previous shots
            start_time = sum(
                s.duration for s in storyboard.shots if s.order < shot.order
            )

            async with async_session_factory() as session:
                track = AudioTrack(
                    project_id=project_id,
                    shot_id=shot.id,
                    name=f"配音 — {shot.title or f'镜头{shot.order + 1}'}",
                    type=AudioType.voice,
                    audio_url=url,
                    duration=shot.duration,
                    volume=1.0,
                    start_time=start_time,
                )
                session.add(track)
                await session.commit()

        except Exception:
            pass  # Continue on failure
