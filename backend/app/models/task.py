"""AsyncTask and OperationLog ORM models."""
from sqlalchemy import String, Text, Float, ForeignKey, Enum as SAEnum, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.models import Base, gen_uuid, TimestampMixin
import enum


class TaskStatus(str, enum.Enum):
    queued = "queued"
    running = "running"
    done = "done"
    failed = "failed"


class TaskType(str, enum.Enum):
    parse_story = "parse_story"
    generate_assets = "generate_assets"
    generate_keyframes = "generate_keyframes"
    generate_animation = "generate_animation"
    generate_audio = "generate_audio"
    compose_video = "compose_video"
    full_pipeline = "full_pipeline"


class AsyncTask(Base, TimestampMixin):
    __tablename__ = "async_tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    task_type: Mapped[TaskType] = mapped_column(
        SAEnum(TaskType), nullable=False
    )
    status: Mapped[TaskStatus] = mapped_column(
        SAEnum(TaskStatus), default=TaskStatus.queued, nullable=False
    )
    progress: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    current_step: Mapped[str] = mapped_column(String(512), default="", nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    input_data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    output_data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    parent_task_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    project = relationship("Project", back_populates="tasks")


class OperationLog(Base, TimestampMixin):
    __tablename__ = "operation_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    before_state: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    after_state: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    project = relationship("Project", back_populates="op_logs")
