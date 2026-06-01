"""Character and Scene asset ORM models."""
from sqlalchemy import String, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models import Base, gen_uuid, TimestampMixin
import enum


class AssetStatus(str, enum.Enum):
    pending = "pending"
    generating = "generating"
    done = "done"
    failed = "failed"


class Character(Base, TimestampMixin):
    __tablename__ = "characters"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    appearance: Mapped[str] = mapped_column(Text, default="", nullable=False)
    personality: Mapped[str] = mapped_column(Text, default="", nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    thumbnail_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    reference_prompt: Mapped[str] = mapped_column(Text, default="", nullable=False)
    status: Mapped[AssetStatus] = mapped_column(
        SAEnum(AssetStatus), default=AssetStatus.pending, nullable=False
    )

    # Relationships
    project = relationship("Project", back_populates="characters")
    voice_profile = relationship("VoiceProfile", back_populates="character", uselist=False)


class Scene(Base, TimestampMixin):
    __tablename__ = "scenes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    setting: Mapped[str] = mapped_column(Text, default="", nullable=False)
    time_of_day: Mapped[str] = mapped_column(String(32), default="白天", nullable=False)
    weather: Mapped[str] = mapped_column(String(32), default="晴朗", nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    thumbnail_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    reference_prompt: Mapped[str] = mapped_column(Text, default="", nullable=False)
    status: Mapped[AssetStatus] = mapped_column(
        SAEnum(AssetStatus), default=AssetStatus.pending, nullable=False
    )

    project = relationship("Project", back_populates="scenes")
