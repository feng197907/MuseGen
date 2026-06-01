"""Export API routes."""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pathlib import Path
from app.core.database import get_db
from app.models.project import Project
from app.models.task import AsyncTask, TaskType
from app.schemas.export import ComposeRequest
from app.schemas.task import AsyncTaskResponse
from app.schemas import ApiResponse
from app.tasks.compose_video import run_compose_video

router = APIRouter()


@router.post("/compose", response_model=ApiResponse[AsyncTaskResponse])
async def compose_video(body: ComposeRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(Project).where(Project.id == body.project_id)
    result = await db.execute(stmt)
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")

    task = AsyncTask(
        project_id=body.project_id,
        task_type=TaskType.compose_video,
        status="queued",
        input_data=body.model_dump(),
    )
    db.add(task)
    await db.flush()
    await db.refresh(task)

    run_compose_video.delay(str(task.id), body.project_id)
    return ApiResponse(data=AsyncTaskResponse.model_validate(task))


@router.get("/{task_id}/download")
async def download_video(task_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(AsyncTask).where(AsyncTask.id == task_id)
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()
    if not task or task.status != "done":
        raise HTTPException(status_code=404, detail="Video not ready")

    output_path = task.output_data.get("output_path", "")
    if not output_path or not Path(output_path).exists():
        raise HTTPException(status_code=404, detail="Video file not found")

    return FileResponse(
        output_path,
        media_type="video/mp4",
        filename=f"musegen_{task.project_id}.mp4",
    )
