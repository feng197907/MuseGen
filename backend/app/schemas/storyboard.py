"""Storyboard/Shot Pydantic schemas."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ShotResponse(BaseModel):
    id: str
    storyboard_id: str
    order: int
    title: str
    description: str
    dialogue: str
    shot_type: str
    camera_movement: str
    duration: float
    mood: str
    prompt_override: Optional[str]
    character_ids: list[str]
    scene_id: Optional[str]
    keyframe_id: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ShotUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    dialogue: Optional[str] = None
    shot_type: Optional[str] = None
    camera_movement: Optional[str] = None
    duration: Optional[float] = None
    mood: Optional[str] = None
    prompt_override: Optional[str] = None
    character_ids: Optional[list[str]] = None
    scene_id: Optional[str] = None


class ShotReorder(BaseModel):
    shot_ids: list[str]


class StoryboardResponse(BaseModel):
    id: str
    project_id: str
    shots: list[ShotResponse]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
