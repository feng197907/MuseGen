"""Generation task request/response schemas."""
from typing import Optional
from pydantic import BaseModel


class ParseStoryRequest(BaseModel):
    project_id: str
    story_text: str


class GenerateAssetsRequest(BaseModel):
    project_id: str
    character_ids: Optional[list[str]] = None
    scene_ids: Optional[list[str]] = None


class GenerateKeyframesRequest(BaseModel):
    project_id: str
    shot_ids: Optional[list[str]] = None


class GenerateAnimationRequest(BaseModel):
    project_id: str
    shot_ids: Optional[list[str]] = None


class GenerateAudioRequest(BaseModel):
    project_id: str
    shot_ids: Optional[list[str]] = None


class FullPipelineRequest(BaseModel):
    project_id: str
    story_text: str
