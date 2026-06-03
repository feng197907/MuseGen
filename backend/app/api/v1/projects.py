"""Projects API routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete as sa_delete
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.schemas import ApiResponse
from app.models.task import OperationLog, AsyncTask
from app.models.asset import Character, Scene
from app.models.storyboard import Storyboard, Shot
from app.models.keyframe import KeyFrame
from app.models.animation import Animation
from app.models.audio import AudioTrack

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
    import logging
    logger = logging.getLogger(__name__)

    stmt = select(Project).where(Project.id == project_id)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        # Explicitly delete all related records in dependency order (bottom-up)
        # so we don't rely on DB-level CASCADE which may be missing.
        # 1. Animations (depend on keyframes)
        await db.execute(
            sa_delete(Animation).where(
                Animation.keyframe_id.in_(
                    select(KeyFrame.id).join(Shot).join(Storyboard)
                    .where(Storyboard.project_id == project_id)
                )
            )
        )
        # 2. KeyFrames (depend on shots)
        await db.execute(
            sa_delete(KeyFrame).where(
                KeyFrame.shot_id.in_(
                    select(Shot.id).join(Storyboard)
                    .where(Storyboard.project_id == project_id)
                )
            )
        )
        # 3. Shots (depend on storyboard)
        await db.execute(
            sa_delete(Shot).where(
                Shot.storyboard_id.in_(
                    select(Storyboard.id).where(Storyboard.project_id == project_id)
                )
            )
        )
        # 4. Storyboard
        await db.execute(sa_delete(Storyboard).where(Storyboard.project_id == project_id))
        # 5. AudioTracks
        await db.execute(sa_delete(AudioTrack).where(AudioTrack.project_id == project_id))
        # 6. Characters
        await db.execute(sa_delete(Character).where(Character.project_id == project_id))
        # 7. Scenes
        await db.execute(sa_delete(Scene).where(Scene.project_id == project_id))
        # 8. AsyncTasks
        await db.execute(sa_delete(AsyncTask).where(AsyncTask.project_id == project_id))
        # 9. OperationLogs
        await db.execute(sa_delete(OperationLog).where(OperationLog.project_id == project_id))
        # 10. Finally, delete the project itself
        await db.delete(project)
        await db.flush()
    except Exception as e:
        logger.error(f"Failed to delete project {project_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

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
