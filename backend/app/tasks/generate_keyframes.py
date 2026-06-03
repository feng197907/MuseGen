"""Celery Task: Generate keyframes for each shot via SDXL + IP-Adapter."""
import asyncio
import logging
from app.tasks.celery_app import celery_app
from app.services.consistency_service import generate_consistent_keyframe
from app.services.image_service import generate_image
from app.services.llm_service import generate_shot_prompt
from app.core.storage import upload_bytes
from app.utils.progress import update_progress
from app.core.database import async_session_factory
from app.models.storyboard import Shot, ShotStatus
from app.models.keyframe import KeyFrame
from app.models.asset import Character, Scene
from sqlalchemy import select
from sqlalchemy.orm import selectinload


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def run_generate_keyframes(
    self, task_id: str, project_id: str, shot_ids: list = None, chain_result=None
):
    """Generate keyframe images for all shots in a project."""
    if chain_result and isinstance(chain_result, dict):
        project_id = chain_result.get("project_id", project_id)

    update_progress(task_id, "generate_keyframes", "running", 5, "Loading storyboard data...")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(_generate_keyframes(task_id, project_id, shot_ids or []))

    update_progress(task_id, "generate_keyframes", "done", 100, "Keyframes generated")
    return {"project_id": project_id, "task_id": task_id}


async def _generate_keyframes(task_id: str, project_id: str, shot_ids: list):
    """Generate keyframe for each shot."""
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

        shots = storyboard.shots
        if shot_ids:
            shots = [s for s in shots if s.id in shot_ids]

    total = max(len(shots), 1)
    for idx, shot in enumerate(shots):
        try:
            update_progress(
                task_id, "generate_keyframes", "running",
                5 + int(90 * idx / total),
                f"Generating keyframe {idx + 1}/{total}: {shot.title}",
            )

            # Fetch characters for this shot
            character_descriptions = []
            primary_ref_url = None

            if shot.character_ids:
                async with async_session_factory() as session:
                    char_stmt = select(Character).where(Character.id.in_(shot.character_ids))
                    char_result = await session.execute(char_stmt)
                    chars = char_result.scalars().all()
                    character_descriptions = [c.appearance for c in chars]
                    # Use first character with image as reference
                    for c in chars:
                        if c.image_url:
                            primary_ref_url = c.image_url
                            break

            # Fetch scene description
            scene_description = ""
            if shot.scene_id:
                async with async_session_factory() as session:
                    scene_stmt = select(Scene).where(Scene.id == shot.scene_id)
                    scene_result = await session.execute(scene_stmt)
                    scene = scene_result.scalar_one_or_none()
                    if scene:
                        scene_description = scene.reference_prompt or scene.description

            # Build prompt
            if shot.prompt_override:
                prompt = shot.prompt_override
            else:
                prompt = generate_shot_prompt(
                    shot.description,
                    character_descriptions,
                    scene_description,
                    shot.shot_type,
                    shot.mood,
                )

            negative_prompt = "low quality, blurry, bad anatomy, watermark, text, nsfw"

            # Generate image (with reference if available)
            if primary_ref_url:
                image_bytes = generate_consistent_keyframe(
                    prompt=prompt,
                    character_image_url=primary_ref_url,
                    negative_prompt=negative_prompt,
                    ip_adapter_scale=0.6,
                    width=512,
                    height=512,
                )
            else:
                image_bytes = generate_image(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    width=512,
                    height=512,
                )

            # Upload
            url = upload_bytes(image_bytes, project_id, "keyframe", "png", "image/png")

            # Save keyframe to DB (upsert — update if exists, insert if new)
            async with async_session_factory() as session:
                kf_stmt = select(KeyFrame).where(KeyFrame.shot_id == shot.id)
                kf_result = await session.execute(kf_stmt)
                existing_kf = kf_result.scalar_one_or_none()
                if existing_kf:
                    existing_kf.image_url = url
                    existing_kf.thumbnail_url = url
                    existing_kf.prompt = prompt
                    existing_kf.width = 512
                    existing_kf.height = 512
                else:
                    kf = KeyFrame(
                        shot_id=shot.id,
                        image_url=url,
                        thumbnail_url=url,
                        prompt=prompt,
                        width=512,
                        height=512,
                    )
                    session.add(kf)

                # Update shot status
                shot_stmt = select(Shot).where(Shot.id == shot.id)
                shot_result = await session.execute(shot_stmt)
                db_shot = shot_result.scalar_one_or_none()
                if db_shot:
                    db_shot.status = ShotStatus.done

                await session.commit()

        except Exception as e:
            logging.getLogger(__name__).error(
                f"Keyframe generation failed for shot {shot.id} ({shot.title}): {e}", exc_info=True
            )
            async with async_session_factory() as session:
                shot_stmt = select(Shot).where(Shot.id == shot.id)
                shot_result = await session.execute(shot_stmt)
                db_shot = shot_result.scalar_one_or_none()
                if db_shot:
                    db_shot.status = ShotStatus.failed
                    await session.commit()
