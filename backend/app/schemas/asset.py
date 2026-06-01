"""Asset Pydantic schemas."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CharacterResponse(BaseModel):
    id: str
    project_id: str
    name: str
    description: str
    appearance: str
    personality: str
    image_url: Optional[str]
    thumbnail_url: Optional[str]
    reference_prompt: str
    voice_profile_id: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SceneResponse(BaseModel):
    id: str
    project_id: str
    name: str
    description: str
    setting: str
    time_of_day: str
    weather: str
    image_url: Optional[str]
    thumbnail_url: Optional[str]
    reference_prompt: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
