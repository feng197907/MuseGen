"""Storyboards API routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.models.storyboard import Storyboard, Shot
from app.schemas.storyboard import StoryboardResponse, ShotUpdate, ShotReorder, ShotResponse
from app.schemas import ApiResponse

router = APIRouter()


@router.get("/{project_id}", response_model=ApiResponse[StoryboardResponse])
async def get_storyboard(project_id: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Storyboard)
        .where(Storyboard.project_id == project_id)
        .options(
            selectinload(Storyboard.shots).selectinload(Shot.keyframe),
        )
    )
    result = await db.execute(stmt)
    sb = result.scalar_one_or_none()
    if not sb:
        raise HTTPException(status_code=404, detail="Storyboard not found")

    # Inject keyframe_id into each shot
    shots = []
    for shot in sb.shots:
        sdata = ShotResponse.model_validate(shot)
        if shot.keyframe:
            sdata.keyframe_id = shot.keyframe.id
        shots.append(sdata)

    resp = StoryboardResponse(
        id=sb.id,
        project_id=sb.project_id,
        shots=shots,
        created_at=sb.created_at,
        updated_at=sb.updated_at,
    )
    return ApiResponse(data=resp)


@router.patch("/shots/{shot_id}", response_model=ApiResponse[ShotResponse])
async def update_shot(shot_id: str, body: ShotUpdate, db: AsyncSession = Depends(get_db)):
    stmt = select(Shot).where(Shot.id == shot_id).options(selectinload(Shot.keyframe))
    result = await db.execute(stmt)
    shot = result.scalar_one_or_none()
    if not shot:
        raise HTTPException(status_code=404, detail="Shot not found")

    update_data = body.model_dump(exclude_none=True)
    for key, val in update_data.items():
        setattr(shot, key, val)

    await db.flush()
    await db.refresh(shot)
    resp = ShotResponse.model_validate(shot)
    if shot.keyframe:
        resp.keyframe_id = shot.keyframe.id
    return ApiResponse(data=resp)


@router.post("/shots/reorder", response_model=ApiResponse[None])
async def reorder_shots(body: ShotReorder, db: AsyncSession = Depends(get_db)):
    if not body.shot_ids:
        raise HTTPException(status_code=400, detail="Empty shot_ids list")

    stmt = select(Shot).where(Shot.id.in_(body.shot_ids))
    result = await db.execute(stmt)
    shots = {s.id: s for s in result.scalars().all()}

    for idx, sid in enumerate(body.shot_ids):
        shot = shots.get(sid)
        if shot:
            shot.order = idx

    await db.flush()
    return ApiResponse(message="Shots reordered")
