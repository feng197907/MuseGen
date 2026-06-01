"""AsyncTask Pydantic schema."""
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel


class AsyncTaskResponse(BaseModel):
    id: str
    project_id: str
    task_type: str
    status: str
    progress: float
    current_step: str
    error_message: Optional[str]
    input_data: dict[str, Any]
    output_data: dict[str, Any]
    created_at: datetime
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    parent_task_id: Optional[str]

    model_config = {"from_attributes": True}
