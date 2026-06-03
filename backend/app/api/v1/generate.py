"""Generate API routes — trigger Celery tasks."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.project import Project
from app.models.task import AsyncTask, TaskType
from app.schemas.generation import (
    ParseStoryRequest,
    GenerateAssetsRequest,
    GenerateKeyframesRequest,
    GenerateAnimationRequest,
    GenerateAudioRequest,
    FullPipelineRequest,
)
from app.schemas.task import AsyncTaskResponse
from app.schemas import ApiResponse
from app.tasks.parse_story import run_parse_story
from app.tasks.generate_assets import run_generate_assets
from app.tasks.generate_keyframes import run_generate_keyframes
from app.tasks.generate_animation import run_generate_animation
from app.tasks.generate_audio import run_generate_audio
from app.tasks.compose_video import run_compose_video

router = APIRouter()


async def _create_task(
    db: AsyncSession,
    project_id: str,
    task_type: TaskType,
    input_data: dict,
) -> AsyncTask:
    task = AsyncTask(
        project_id=project_id,
        task_type=task_type,
        status="queued",
        input_data=input_data,
    )
    db.add(task)
    await db.flush()
    await db.refresh(task)
    return task


@router.post("/parse-story", response_model=ApiResponse[AsyncTaskResponse])
async def parse_story(body: ParseStoryRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(Project).where(Project.id == body.project_id)
    result = await db.execute(stmt)
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")

    task = await _create_task(db, body.project_id, TaskType.parse_story, body.model_dump())
    run_parse_story.delay(str(task.id), body.project_id, body.story_text)
    return ApiResponse(data=AsyncTaskResponse.model_validate(task))


@router.post("/assets", response_model=ApiResponse[AsyncTaskResponse])
async def generate_assets(body: GenerateAssetsRequest, db: AsyncSession = Depends(get_db)):
    task = await _create_task(db, body.project_id, TaskType.generate_assets, body.model_dump())
    run_generate_assets.delay(str(task.id), body.project_id)
    return ApiResponse(data=AsyncTaskResponse.model_validate(task))


@router.post("/keyframes", response_model=ApiResponse[AsyncTaskResponse])
async def generate_keyframes(body: GenerateKeyframesRequest, db: AsyncSession = Depends(get_db)):
    task = await _create_task(db, body.project_id, TaskType.generate_keyframes, body.model_dump())
    run_generate_keyframes.delay(str(task.id), body.project_id, body.shot_ids or [])
    return ApiResponse(data=AsyncTaskResponse.model_validate(task))


@router.post("/animation", response_model=ApiResponse[AsyncTaskResponse])
async def generate_animation(body: GenerateAnimationRequest, db: AsyncSession = Depends(get_db)):
    task = await _create_task(db, body.project_id, TaskType.generate_animation, body.model_dump())
    run_generate_animation.delay(str(task.id), body.project_id, body.shot_ids or [])
    return ApiResponse(data=AsyncTaskResponse.model_validate(task))


@router.post("/audio", response_model=ApiResponse[AsyncTaskResponse])
async def generate_audio(body: GenerateAudioRequest, db: AsyncSession = Depends(get_db)):
    task = await _create_task(db, body.project_id, TaskType.generate_audio, body.model_dump())
    run_generate_audio.delay(str(task.id), body.project_id, body.shot_ids or [])
    return ApiResponse(data=AsyncTaskResponse.model_validate(task))


@router.post("/full-pipeline", response_model=ApiResponse[AsyncTaskResponse])
async def full_pipeline(body: FullPipelineRequest, db: AsyncSession = Depends(get_db)):
    """Orchestrates the full 6-step pipeline in sequence."""
    stmt = select(Project).where(Project.id == body.project_id)
    result = await db.execute(stmt)
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")

    task = await _create_task(db, body.project_id, TaskType.full_pipeline, body.model_dump())

    # Chain: parse → assets → keyframes → animation → audio → compose
    # .si() (immutable) prevents Celery from prepending the previous task's
    # return value, so each task gets exactly the args specified.
    from celery import chain
    tid = str(task.id)
    pid = body.project_id
    pipeline = chain(
        run_parse_story.s(tid, pid, body.story_text),
        run_generate_assets.si(tid, pid),
        run_generate_keyframes.si(tid, pid),
        run_generate_animation.si(tid, pid),
        run_generate_audio.si(tid, pid),
        run_compose_video.si(tid, pid),
    )
    pipeline.apply_async()
    return ApiResponse(data=AsyncTaskResponse.model_validate(task))
