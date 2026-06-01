"""Celery Task: Generate animation clips from keyframes via SVD."""
import asyncio
from app.tasks.celery_app import celery_app
from app.services.video_service import generate_video_from_image
from app.core.storage import upload_bytes
from app.utils.progress import update_progress
from app.core.database import async_session_factory
from app.models.keyframe import KeyFrame
from app.models.animation import Animation
from app.models.storyboard import Shot
from sqlalchemy import select
from sqlalchemy.orm import selectinload


@celery_app.task(bind=True, max_retries=2, default_retry_delay=120)
def run_generate_animation(
    self, task_id: str, project_id: str, shot_ids: list = None, chain_result=None
):
    """Generate animation clips for all keyframes in a project."""
    if chain_result and isinstance(chain_result, dict):
        project_id = chain_result.get("project_id", project_id)

    update_progress(task_id, "generate_animation", "running", 5, "Loading keyframes...")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(_generate_animations(task_id, project_id, shot_ids or []))

    update_progress(task_id, "generate_animation", "done", 100, "Animations generated")
    return {"project_id": project_id, "task_id": task_id}


async def _generate_animations(task_id: str, project_id: str, shot_ids: list):
    """Iterate over keyframes and generate animation for each."""
    async with async_session_factory() as session:
        from app.models.storyboard import Storyboard
        stmt = (
            select(Storyboard)
            .where(Storyboard.project_id == project_id)
            .options(
                selectinload(Storyboard.shots).selectinload(Shot.keyframe)
            )
        )
        result = await session.execute(stmt)
        storyboard = result.scalar_one_or_none()

        if not storyboard:
            return

        shots = [s for s in storyboard.shots if s.keyframe]
        if shot_ids:
            shots = [s for s in shots if s.id in shot_ids]

    total = max(len(shots), 1)
    for idx, shot in enumerate(shots):
        kf = shot.keyframe
        if not kf or not kf.image_url:
            continue

        try:
            update_progress(
                task_id, "generate_animation", "running",
                5 + int(90 * idx / total),
                f"Animating frame {idx + 1}/{total}",
            )

            video_bytes = generate_video_from_image(
                image_url=kf.image_url,
                num_frames=25,
                fps=6,
                motion_bucket_id=127,
            )

            url = upload_bytes(video_bytes, project_id, "animation", "mp4", "video/mp4")

            async with async_session_factory() as session:
                anim = Animation(
                    keyframe_id=kf.id,
                    video_url=url,
                    duration=shot.duration,
                    fps=6,
                )
                session.add(anim)
                await session.commit()

        except Exception:
            pass  # Log and continue; don't fail the whole task
