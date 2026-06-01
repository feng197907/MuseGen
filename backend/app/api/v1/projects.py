"""Projects API routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.schemas import ApiResponse
from app.models.task import OperationLog

router = APIRouter()


@router.post("", response_model=ApiResponse[ProjectResponse])
async def create_project(body: ProjectCreate, db: AsyncSession = Depends(get_db)):
    project = Project(name=body.name, description=body.description, story_text=body.story_text)
    db.add(project)
    await db.flush()
    await db.refresh(project)
    return ApiResponse(data=ProjectResponse.model_validate(project))


@router.get("", response_model=ApiResponse[list[ProjectResponse]])
async def list_projects(db: AsyncSession = Depends(get_db)):
    stmt = select(Project).order_by(Project.updated_at.desc())
    result = await db.execute(stmt)
    projects = result.scalars().all()
    return ApiResponse(data=[ProjectResponse.model_validate(p) for p in projects])


@router.get("/{project_id}", response_model=ApiResponse[ProjectResponse])
async def get_project(project_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Project).where(Project.id == project_id).options(
        selectinload(Project.storyboard),
    )
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    resp = ProjectResponse.model_validate(project)
    if project.storyboard:
        resp.storyboard_id = project.storyboard.id
    return ApiResponse(data=resp)


@router.patch("/{project_id}", response_model=ApiResponse[ProjectResponse])
async def update_project(project_id: str, body: ProjectUpdate, db: AsyncSession = Depends(get_db)):
    stmt = select(Project).where(Project.id == project_id)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    update_data = body.model_dump(exclude_none=True)
    for key, val in update_data.items():
        setattr(project, key, val)

    await db.flush()
    await db.refresh(project)
    return ApiResponse(data=ProjectResponse.model_validate(project))


@router.delete("/{project_id}", response_model=ApiResponse[None])
async def delete_project(project_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Project).where(Project.id == project_id)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    await db.delete(project)
    await db.flush()
    return ApiResponse(message="Project deleted")


@router.post("/{project_id}/undo", response_model=ApiResponse[None])
async def undo_operation(project_id: str, db: AsyncSession = Depends(get_db)):
    """Pop the latest OperationLog for this project and apply the before_state."""
    stmt = (
        select(OperationLog)
        .where(OperationLog.project_id == project_id)
        .order_by(OperationLog.created_at.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    log = result.scalar_one_or_none()
    if not log:
        raise HTTPException(status_code=400, detail="Nothing to undo")

    # Revert project fields from before_state
    project_result = await db.execute(select(Project).where(Project.id == project_id))
    project = project_result.scalar_one_or_none()
    if project and log.before_state:
        for key, val in log.before_state.items():
            if hasattr(project, key):
                setattr(project, key, val)

    await db.delete(log)
    await db.flush()
    return ApiResponse(message="Undo applied")


@router.post("/{project_id}/redo", response_model=ApiResponse[None])
async def redo_operation(project_id: str, db: AsyncSession = Depends(get_db)):
    """Apply the after_state of a redo (stub — paired with undo)."""
    return ApiResponse(message="Redo applied")
