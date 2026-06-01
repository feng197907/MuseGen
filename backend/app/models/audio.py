"""AudioTrack and VoiceProfile ORM models."""
from sqlalchemy import String, Float, ForeignKey, Enum as SAEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models import Base, gen_uuid, TimestampMixin
import enum


class AudioType(str, enum.Enum):
    voice = "voice"
    bgm = "bgm"
    sfx = "sfx"


class AudioTrack(Base, TimestampMixin):
    __tablename__ = "audio_tracks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    shot_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    type: Mapped[AudioType] = mapped_column(
        SAEnum(AudioType), default=AudioType.voice, nullable=False
    )
    audio_url: Mapped[str] = mapped_column(String(512), nullable=False)
    duration: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    volume: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    start_time: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    project = relationship("Project", back_populates="audio_tracks")


class TTSProvider(str, enum.Enum):
    elevenlabs = "elevenlabs"
    volcano = "volcano"


class VoiceProfile(Base, TimestampMixin):
    __tablename__ = "voice_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    character_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("characters.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(256), default="", nullable=False)
    provider: Mapped[TTSProvider] = mapped_column(
        SAEnum(TTSProvider), default=TTSProvider.elevenlabs, nullable=False
    )
    voice_id: Mapped[str] = mapped_column(String(256), nullable=False)
    settings: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    character = relationship("Character", back_populates="voice_profile")
