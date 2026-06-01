"""Project ORM model."""
from sqlalchemy import String, Text, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models import Base, gen_uuid, TimestampMixin
import enum


class ProjectStatus(str, enum.Enum):
    draft = "draft"
    in_progress = "in_progress"
    completed = "completed"


class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    cover_image: Mapped[str | None] = mapped_column(String(512), nullable=True)
    status: Mapped[ProjectStatus] = mapped_column(
        SAEnum(ProjectStatus), default=ProjectStatus.draft, nullable=False
    )
    story_text: Mapped[str] = mapped_column(Text, default="", nullable=False)

    # Relationships
    storyboard = relationship("Storyboard", back_populates="project", uselist=False)
    characters = relationship("Character", back_populates="project")
    scenes = relationship("Scene", back_populates="project")
    audio_tracks = relationship("AudioTrack", back_populates="project")
    tasks = relationship("AsyncTask", back_populates="project")
    op_logs = relationship("OperationLog", back_populates="project")
