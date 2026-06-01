"""Tasks API routes — query async task status."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.task import AsyncTask
from app.schemas.task import AsyncTaskResponse
from app.schemas import ApiResponse

router = APIRouter()


@router.get("/{task_id}", response_model=ApiResponse[AsyncTaskResponse])
async def get_task(task_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(AsyncTask).where(AsyncTask.id == task_id)
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return ApiResponse(data=AsyncTaskResponse.model_validate(task))
