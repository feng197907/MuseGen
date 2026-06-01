"""Storyboard and Shot ORM models."""
from sqlalchemy import String, Text, Integer, Float, ForeignKey, Enum as SAEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models import Base, gen_uuid, TimestampMixin
import enum


class ShotStatus(str, enum.Enum):
    pending = "pending"
    generating = "generating"
    done = "done"
    failed = "failed"


class Storyboard(Base, TimestampMixin):
    __tablename__ = "storyboards"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    project = relationship("Project", back_populates="storyboard")
    shots: Mapped[list["Shot"]] = relationship(
        "Shot", back_populates="storyboard", order_by="Shot.order"
    )


class Shot(Base, TimestampMixin):
    __tablename__ = "shots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    storyboard_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("storyboards.id", ondelete="CASCADE"), nullable=False
    )
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    title: Mapped[str] = mapped_column(String(256), default="", nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    dialogue: Mapped[str] = mapped_column(Text, default="", nullable=False)
    shot_type: Mapped[str] = mapped_column(String(32), default="中景", nullable=False)
    camera_movement: Mapped[str] = mapped_column(String(32), default="固定", nullable=False)
    duration: Mapped[float] = mapped_column(Float, default=5.0, nullable=False)
    mood: Mapped[str] = mapped_column(String(32), default="平静", nullable=False)
    prompt_override: Mapped[str | None] = mapped_column(Text, nullable=True)
    character_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    scene_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    status: Mapped[ShotStatus] = mapped_column(
        SAEnum(ShotStatus), default=ShotStatus.pending, nullable=False
    )

    # Relationships
    storyboard = relationship("Storyboard", back_populates="shots")
    keyframe = relationship("KeyFrame", back_populates="shot", uselist=False)
