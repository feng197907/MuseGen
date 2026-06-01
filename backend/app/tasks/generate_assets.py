"""Celery Task: Generate character and scene assets via SDXL."""
import asyncio
from app.tasks.celery_app import celery_app
from app.services.image_service import generate_image
from app.services.llm_service import generate_shot_prompt
from app.core.storage import upload_bytes
from app.utils.progress import update_progress
from app.core.database import async_session_factory
from app.models.asset import Character, Scene, AssetStatus
from sqlalchemy import select


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def run_generate_assets(self, task_id: str, project_id: str, chain_result=None):
    """Generate character portraits and scene images via SDXL."""
    if chain_result and isinstance(chain_result, dict):
        project_id = chain_result.get("project_id", project_id)

    update_progress(task_id, "generate_assets", "running", 10, "Starting asset generation...")

    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(_generate_all_assets(task_id, project_id))

    update_progress(task_id, "generate_assets", "done", 100, "Assets generated successfully")
    return {"project_id": project_id, "task_id": task_id, "results": results}


async def _generate_all_assets(task_id: str, project_id: str) -> dict:
    """Generate images for all characters and scenes in a project."""
    async with async_session_factory() as session:
        # Characters
        char_stmt = select(Character).where(Character.project_id == project_id)
        char_result = await session.execute(char_stmt)
        characters = char_result.scalars().all()

        # Scenes
        scene_stmt = select(Scene).where(Scene.project_id == project_id)
        scene_result = await session.execute(scene_stmt)
        scenes = scene_result.scalars().all()

    total = len(characters) + len(scenes)
    count = 0

    # Generate characters
    for char in characters:
        try:
            update_progress(
                task_id, "generate_assets", "running",
                10 + int(40 * count / max(total, 1)),
                f"Generating character: {char.name}",
            )
            prompt = f"anime style, high quality, character portrait, {char.appearance}, {char.reference_prompt}, full body, detailed design, white background"
            image_bytes = generate_image(prompt=prompt, width=768, height=1024)
            url = upload_bytes(image_bytes, project_id, "character", "png", "image/png")

            async with async_session_factory() as session:
                stmt = select(Character).where(Character.id == char.id)
                result = await session.execute(stmt)
                db_char = result.scalar_one_or_none()
                if db_char:
                    db_char.image_url = url
                    db_char.thumbnail_url = url  # Same for now
                    db_char.status = AssetStatus.done
                    await session.commit()

            count += 1
        except Exception as e:
            async with async_session_factory() as session:
                stmt = select(Character).where(Character.id == char.id)
                result = await session.execute(stmt)
                db_char = result.scalar_one_or_none()
                if db_char:
                    db_char.status = AssetStatus.failed
                    await session.commit()
            count += 1

    # Generate scenes
    for scene in scenes:
        try:
            update_progress(
                task_id, "generate_assets", "running",
                50 + int(40 * (count - len(characters)) / max(len(scenes), 1)),
                f"Generating scene: {scene.name}",
            )
            prompt = f"anime style, high quality, background art, {scene.reference_prompt}, {scene.setting}, {scene.time_of_day}, {scene.weather}, detailed environment, anime background"
            image_bytes = generate_image(prompt=prompt, width=1024, height=576)
            url = upload_bytes(image_bytes, project_id, "scene", "png", "image/png")

            async with async_session_factory() as session:
                stmt = select(Scene).where(Scene.id == scene.id)
                result = await session.execute(stmt)
                db_scene = result.scalar_one_or_none()
                if db_scene:
                    db_scene.image_url = url
                    db_scene.thumbnail_url = url
                    db_scene.status = AssetStatus.done
                    await session.commit()

            count += 1
        except Exception as e:
            async with async_session_factory() as session:
                stmt = select(Scene).where(Scene.id == scene.id)
                result = await session.execute(stmt)
                db_scene = result.scalar_one_or_none()
                if db_scene:
                    db_scene.status = AssetStatus.failed
                    await session.commit()
            count += 1

    return {"characters_done": len(characters), "scenes_done": len(scenes)}


# Standalone function for single-character regeneration (called via API)
@celery_app.task(bind=True, max_retries=2, default_retry_delay=30)
def trigger_regenerate_character(self, character_id: str):
    """Regenerate a single character portrait."""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_regenerate_single_character(character_id))


async def _regenerate_single_character(character_id: str):
    """Re-run image generation for one character."""
    async with async_session_factory() as session:
        stmt = select(Character).where(Character.id == character_id)
        result = await session.execute(stmt)
        char = result.scalar_one_or_none()

    if not char:
        return

    try:
        prompt = f"anime style, high quality, character portrait, {char.appearance}, {char.reference_prompt}, full body, detailed design, white background"
        image_bytes = generate_image(prompt=prompt, width=768, height=1024)
        url = upload_bytes(image_bytes, char.project_id, "character", "png", "image/png")

        async with async_session_factory() as session:
            stmt = select(Character).where(Character.id == character_id)
            result = await session.execute(stmt)
            db_char = result.scalar_one_or_none()
            if db_char:
                db_char.image_url = url
                db_char.thumbnail_url = url
                db_char.status = AssetStatus.done
                await session.commit()
    except Exception:
        async with async_session_factory() as session:
            stmt = select(Character).where(Character.id == character_id)
            result = await session.execute(stmt)
            db_char = result.scalar_one_or_none()
            if db_char:
                db_char.status = AssetStatus.failed
                await session.commit()
