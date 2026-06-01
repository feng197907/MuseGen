"""Assets API routes."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.asset import Character, Scene
from app.schemas.asset import CharacterResponse, SceneResponse
from app.schemas import ApiResponse
from app.tasks.generate_assets import trigger_regenerate_character

router = APIRouter()


@router.get("/characters", response_model=ApiResponse[list[CharacterResponse]])
async def list_characters(
    project_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Character).where(Character.project_id == project_id).order_by(Character.created_at)
    result = await db.execute(stmt)
    chars = result.scalars().all()
    return ApiResponse(data=[CharacterResponse.model_validate(c) for c in chars])


@router.get("/scenes", response_model=ApiResponse[list[SceneResponse]])
async def list_scenes(
    project_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Scene).where(Scene.project_id == project_id).order_by(Scene.created_at)
    result = await db.execute(stmt)
    scenes = result.scalars().all()
    return ApiResponse(data=[SceneResponse.model_validate(s) for s in scenes])


@router.post("/characters/{character_id}/regenerate", response_model=ApiResponse[CharacterResponse])
async def regenerate_character(character_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Character).where(Character.id == character_id)
    result = await db.execute(stmt)
    char = result.scalar_one_or_none()
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")

    char.status = "generating"
    await db.flush()

    # Trigger async regeneration
    trigger_regenerate_character.delay(character_id)

    await db.refresh(char)
    return ApiResponse(data=CharacterResponse.model_validate(char))
