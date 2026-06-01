"""Celery Task: Compose final video using FFmpeg."""
import asyncio
import httpx
import tempfile
from pathlib import Path
from app.tasks.celery_app import celery_app
from app.services.ffmpeg_service import compose_video
from app.core.storage import upload_file
from app.utils.progress import update_progress
from app.utils.file_utils import TempDir
from app.core.database import async_session_factory
from app.models.storyboard import Shot
from app.models.keyframe import KeyFrame
from app.models.animation import Animation
from app.models.audio import AudioTrack
from app.models.task import AsyncTask, TaskStatus
from app.models.project import Project, ProjectStatus
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import datetime


@celery_app.task(bind=True, max_retries=2, default_retry_delay=60)
def run_compose_video(self, task_id: str, project_id: str, chain_result=None):
    """Compose all animation clips and audio tracks into final MP4."""
    if chain_result and isinstance(chain_result, dict):
        project_id = chain_result.get("project_id", project_id)

    update_progress(task_id, "compose_video", "running", 5, "Loading assets for composition...")

    loop = asyncio.get_event_loop()
    output_url = loop.run_until_complete(_compose(task_id, project_id))

    update_progress(task_id, "compose_video", "done", 100, "Video composition complete!")

    # Save output path in task record
    loop.run_until_complete(_save_task_output(task_id, output_url))
    loop.run_until_complete(_set_project_completed(project_id))

    return {"project_id": project_id, "task_id": task_id, "output_url": output_url}


async def _compose(task_id: str, project_id: str) -> str:
    """Fetch all assets and invoke FFmpeg."""
    async with async_session_factory() as session:
        from app.models.storyboard import Storyboard
        stmt = (
            select(Storyboard)
            .where(Storyboard.project_id == project_id)
            .options(
                selectinload(Storyboard.shots)
                .selectinload(Shot.keyframe)
                .selectinload(KeyFrame.animation)
            )
        )
        result = await session.execute(stmt)
        storyboard = result.scalar_one_or_none()

        # Audio tracks
        audio_stmt = select(AudioTrack).where(AudioTrack.project_id == project_id).order_by(AudioTrack.start_time)
        audio_result = await session.execute(audio_stmt)
        db_audio_tracks = audio_result.scalars().all()

    if not storyboard:
        raise ValueError(f"No storyboard found for project {project_id}")

    shots = sorted(storyboard.shots, key=lambda s: s.order)

    with TempDir() as tmp_dir:
        tmp_path = Path(tmp_dir)
        video_clip_paths = []
        update_progress(task_id, "compose_video", "running", 20, "Downloading video clips...")

        for idx, shot in enumerate(shots):
            kf = shot.keyframe
            if not kf:
                continue
            anim = kf.animation
            if not anim or not anim.video_url:
                continue

            # Download video clip
            clip_path = tmp_path / f"clip_{idx:04d}.mp4"
            async with httpx.AsyncClient(timeout=120) as http:
                resp = await http.get(anim.video_url)
                resp.raise_for_status()
                clip_path.write_bytes(resp.content)
            video_clip_paths.append(str(clip_path))

        if not video_clip_paths:
            raise ValueError("No video clips available for composition")

        update_progress(task_id, "compose_video", "running", 50, "Downloading audio tracks...")

        audio_track_params = []
        for idx, track in enumerate(db_audio_tracks):
            audio_path = tmp_path / f"audio_{idx:04d}.mp3"
            async with httpx.AsyncClient(timeout=60) as http:
                resp = await http.get(track.audio_url)
                resp.raise_for_status()
                audio_path.write_bytes(resp.content)
            audio_track_params.append({
                "path": str(audio_path),
                "volume": track.volume,
                "start_time": track.start_time,
                "type": track.type,
            })

        update_progress(task_id, "compose_video", "running", 70, "Running FFmpeg composition...")

        output_path = tmp_path / "final_output.mp4"
        compose_video(
            video_clips=video_clip_paths,
            audio_tracks=audio_track_params,
            output_path=str(output_path),
        )

        update_progress(task_id, "compose_video", "running", 90, "Uploading final video...")

        output_url = upload_file(str(output_path), project_id, "export", "mp4")

    return output_url


async def _save_task_output(task_id: str, output_url: str):
    """Persist the output URL and finished status in AsyncTask."""
    async with async_session_factory() as session:
        stmt = select(AsyncTask).where(AsyncTask.id == task_id)
        result = await session.execute(stmt)
        task = result.scalar_one_or_none()
        if task:
            task.status = TaskStatus.done
            task.output_data = {"output_url": output_url}
            task.finished_at = datetime.utcnow()
            task.progress = 100.0
            await session.commit()


async def _set_project_completed(project_id: str):
    """Mark project as completed after successful video export."""
    async with async_session_factory() as session:
        stmt = select(Project).where(Project.id == project_id)
        result = await session.execute(stmt)
        project = result.scalar_one_or_none()
        if project:
            project.status = ProjectStatus.completed
            await session.commit()
