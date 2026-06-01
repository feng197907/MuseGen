"""Export task schemas."""
from pydantic import BaseModel


class ComposeRequest(BaseModel):
    project_id: str
