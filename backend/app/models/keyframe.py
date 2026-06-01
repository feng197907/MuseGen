"""KeyFrame ORM model."""
from sqlalchemy import String, Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models import Base, gen_uuid, TimestampMixin


class KeyFrame(Base, TimestampMixin):
    __tablename__ = "keyframes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    shot_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("shots.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    image_url: Mapped[str] = mapped_column(String(512), nullable=False)
    thumbnail_url: Mapped[str] = mapped_column(String(512), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, default="", nullable=False)
    width: Mapped[int] = mapped_column(Integer, default=1920, nullable=False)
    height: Mapped[int] = mapped_column(Integer, default=1080, nullable=False)

    # Relationships
    shot = relationship("Shot", back_populates="keyframe")
    animation = relationship("Animation", back_populates="keyframe", uselist=False)
