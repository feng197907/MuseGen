"""Initial migration — create all tables.

Revision ID: 0001
Revises: None
Create Date: 2024-01-01 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from app.core.database import Base
from app.models.project import Project  # noqa: F401
from app.models.storyboard import Storyboard, Shot  # noqa: F401
from app.models.asset import Character, Scene  # noqa: F401
from app.models.keyframe import KeyFrame  # noqa: F401
from app.models.animation import Animation  # noqa: F401
from app.models.audio import AudioTrack, VoiceProfile  # noqa: F401
from app.models.task import AsyncTask, OperationLog  # noqa: F401

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all tables."""
    # Using metadata create_all approach for simplicity
    # In production, generate explicit DDL with `alembic revision --autogenerate`
    op.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")

    # Projects
    op.create_table(
        "projects",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("description", sa.Text, nullable=False, server_default=""),
        sa.Column("cover_image", sa.String(512), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="draft"),
        sa.Column("story_text", sa.Text, nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Storyboards
    op.create_table(
        "storyboards",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Shots
    op.create_table(
        "shots",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("storyboard_id", sa.String(36), sa.ForeignKey("storyboards.id", ondelete="CASCADE"), nullable=False),
        sa.Column("order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("title", sa.String(256), nullable=False, server_default=""),
        sa.Column("description", sa.Text, nullable=False, server_default=""),
        sa.Column("dialogue", sa.Text, nullable=False, server_default=""),
        sa.Column("shot_type", sa.String(32), nullable=False, server_default="中景"),
        sa.Column("camera_movement", sa.String(32), nullable=False, server_default="固定"),
        sa.Column("duration", sa.Float, nullable=False, server_default="5.0"),
        sa.Column("mood", sa.String(32), nullable=False, server_default="平静"),
        sa.Column("prompt_override", sa.Text, nullable=True),
        sa.Column("character_ids", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("scene_id", sa.String(36), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Characters
    op.create_table(
        "characters",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("description", sa.Text, nullable=False, server_default=""),
        sa.Column("appearance", sa.Text, nullable=False, server_default=""),
        sa.Column("personality", sa.Text, nullable=False, server_default=""),
        sa.Column("image_url", sa.String(512), nullable=True),
        sa.Column("thumbnail_url", sa.String(512), nullable=True),
        sa.Column("reference_prompt", sa.Text, nullable=False, server_default=""),
        sa.Column("status", sa.String(32), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Scenes
    op.create_table(
        "scenes",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("description", sa.Text, nullable=False, server_default=""),
        sa.Column("setting", sa.Text, nullable=False, server_default=""),
        sa.Column("time_of_day", sa.String(32), nullable=False, server_default="白天"),
        sa.Column("weather", sa.String(32), nullable=False, server_default="晴朗"),
        sa.Column("image_url", sa.String(512), nullable=True),
        sa.Column("thumbnail_url", sa.String(512), nullable=True),
        sa.Column("reference_prompt", sa.Text, nullable=False, server_default=""),
        sa.Column("status", sa.String(32), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Keyframes
    op.create_table(
        "keyframes",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("shot_id", sa.String(36), sa.ForeignKey("shots.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("image_url", sa.String(512), nullable=False),
        sa.Column("thumbnail_url", sa.String(512), nullable=False),
        sa.Column("prompt", sa.Text, nullable=False, server_default=""),
        sa.Column("width", sa.Integer, nullable=False, server_default="1920"),
        sa.Column("height", sa.Integer, nullable=False, server_default="1080"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Animations
    op.create_table(
        "animations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("keyframe_id", sa.String(36), sa.ForeignKey("keyframes.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("video_url", sa.String(512), nullable=False),
        sa.Column("duration", sa.Float, nullable=False, server_default="5.0"),
        sa.Column("fps", sa.Integer, nullable=False, server_default="24"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Audio tracks
    op.create_table(
        "audio_tracks",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("shot_id", sa.String(36), nullable=True),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("type", sa.String(32), nullable=False, server_default="voice"),
        sa.Column("audio_url", sa.String(512), nullable=False),
        sa.Column("duration", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("volume", sa.Float, nullable=False, server_default="1.0"),
        sa.Column("start_time", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Voice profiles
    op.create_table(
        "voice_profiles",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("character_id", sa.String(36), sa.ForeignKey("characters.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("name", sa.String(256), nullable=False, server_default=""),
        sa.Column("provider", sa.String(32), nullable=False, server_default="elevenlabs"),
        sa.Column("voice_id", sa.String(256), nullable=False),
        sa.Column("settings", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Async tasks
    op.create_table(
        "async_tasks",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("task_type", sa.String(64), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="queued"),
        sa.Column("progress", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("current_step", sa.String(512), nullable=False, server_default=""),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("input_data", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("output_data", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("parent_task_id", sa.String(36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Operation logs
    op.create_table(
        "operation_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("action", sa.String(128), nullable=False),
        sa.Column("before_state", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("after_state", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    """Drop all tables."""
    op.drop_table("operation_logs")
    op.drop_table("async_tasks")
    op.drop_table("voice_profiles")
    op.drop_table("audio_tracks")
    op.drop_table("animations")
    op.drop_table("keyframes")
    op.drop_table("scenes")
    op.drop_table("characters")
    op.drop_table("shots")
    op.drop_table("storyboards")
    op.drop_table("projects")
