"""create system_events

Revision ID: 011_create_system_events
Revises: 010_create_refresh_tokens
Create Date: 2026-01-01 00:00:10

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "011_create_system_events"
down_revision: Union[str, None] = "010_create_refresh_tokens"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_event_severity = sa.Enum(
    "debug",
    "info",
    "warning",
    "error",
    "critical",
    name="event_severity",
    native_enum=False,
    length=16,
)


def upgrade() -> None:
    op.create_table(
        "system_events",
        sa.Column(
            "id",
            sa.Uuid(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("severity", _event_severity, nullable=False),
        sa.Column("message", sa.String(length=512), nullable=False),
        sa.Column("request_id", sa.String(length=64), nullable=True),
        sa.Column(
            "metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_system_events"),
    )
    op.create_index("ix_system_events_event_type", "system_events", ["event_type"])
    op.create_index("ix_system_events_severity", "system_events", ["severity"])


def downgrade() -> None:
    op.drop_index("ix_system_events_severity", table_name="system_events")
    op.drop_index("ix_system_events_event_type", table_name="system_events")
    op.drop_table("system_events")
    bind = op.get_bind()
    _event_severity.drop(bind, checkfirst=True)
