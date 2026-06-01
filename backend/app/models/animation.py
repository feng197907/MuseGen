"""Animation ORM model."""
from sqlalchemy import String, Integer, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models import Base, gen_uuid, TimestampMixin


class Animation(Base, TimestampMixin):
    __tablename__ = "animations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    keyframe_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("keyframes.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    video_url: Mapped[str] = mapped_column(String(512), nullable=False)
    duration: Mapped[float] = mapped_column(Float, default=5.0, nullable=False)
    fps: Mapped[int] = mapped_column(Integer, default=24, nullable=False)

    keyframe = relationship("KeyFrame", back_populates="animation")
