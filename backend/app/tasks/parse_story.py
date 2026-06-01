"""Celery Task: Parse story text into characters, scenes, and shots."""
import json
import asyncio
import time
from pathlib import Path
from app.tasks.celery_app import celery_app
from app.services.llm_service import parse_story as llm_parse
from app.utils.progress import update_progress

# Must import models for create_all to work within the task context
from app.core.database import async_session_factory
from app.models.project import Project, ProjectStatus
from app.models.storyboard import Storyboard, Shot, ShotStatus
from app.models.asset import Character, Scene, AssetStatus


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def run_parse_story(self, task_id: str, project_id: str, story_text: str):
    """Parse story text via LLM and populate the DB with characters, scenes, and shots."""
    update_progress(task_id, "parse_story", "running", 10, "Parsing story text with LLM...")
    self.update_state(state="PROGRESS", meta={"progress": 10, "status": "running"})

    try:
        result = llm_parse(story_text)
    except Exception as e:
        update_progress(task_id, "parse_story", "failed", 0, str(e))
        raise

    update_progress(task_id, "parse_story", "running", 50, "Writing results to database...")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(_save_parse_results(task_id, project_id, result))

    update_progress(task_id, "parse_story", "done", 100, "Story parsed successfully")
    return {"project_id": project_id, "task_id": task_id}


async def _save_parse_results(task_id: str, project_id: str, result: dict):
    """Async helper to persist parsed data."""
    async with async_session_factory() as session:
        # Update project status
        from sqlalchemy import select
        stmt = select(Project).where(Project.id == project_id)
        proj_result = await session.execute(stmt)
        project = proj_result.scalar_one_or_none()
        if project:
            project.status = ProjectStatus.in_progress

        # Create or get storyboard
        stmt_sb = select(Storyboard).where(Storyboard.project_id == project_id)
        sb_result = await session.execute(stmt_sb)
        storyboard = sb_result.scalar_one_or_none()
        if not storyboard:
            storyboard = Storyboard(project_id=project_id)
            session.add(storyboard)
            await session.flush()

        # Create characters
        characters_map = {}
        for char_data in result.get("characters", []):
            char = Character(
                project_id=project_id,
                name=char_data.get("name", "Unknown"),
                description=char_data.get("description", ""),
                appearance=char_data.get("appearance", ""),
                personality=char_data.get("personality", ""),
                reference_prompt=char_data.get("reference_prompt", ""),
                status=AssetStatus.pending,
            )
            session.add(char)
            await session.flush()
            characters_map[char.name] = char.id

        # Create scenes
        scenes_map = {}
        for scene_data in result.get("scenes", []):
            scene = Scene(
                project_id=project_id,
                name=scene_data.get("name", "Unknown"),
                description=scene_data.get("description", ""),
                setting=scene_data.get("setting", ""),
                time_of_day=scene_data.get("time_of_day", "白天"),
                weather=scene_data.get("weather", "晴朗"),
                reference_prompt=scene_data.get("reference_prompt", ""),
                status=AssetStatus.pending,
            )
            session.add(scene)
            await session.flush()
            scenes_map[scene.name] = scene.id

        # Create shots
        for idx, shot_data in enumerate(result.get("shots", [])):
            char_names = shot_data.get("character_names", [])
            scene_name = shot_data.get("scene_name", "")

            char_ids = [characters_map.get(n) for n in char_names if characters_map.get(n)]
            scene_id = scenes_map.get(scene_name)

            shot = Shot(
                storyboard_id=storyboard.id,
                order=idx,
                title=shot_data.get("title", f"镜头 {idx + 1}"),
                description=shot_data.get("description", ""),
                dialogue=shot_data.get("dialogue", ""),
                shot_type=shot_data.get("shot_type", "中景"),
                camera_movement=shot_data.get("camera_movement", "固定"),
                duration=float(shot_data.get("duration", 5.0)),
                mood=shot_data.get("mood", "平静"),
                character_ids=char_ids,
                scene_id=scene_id,
                status=ShotStatus.pending,
            )
            session.add(shot)

        await session.commit()
