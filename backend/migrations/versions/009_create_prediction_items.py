"""create prediction_items

Revision ID: 009_create_prediction_items
Revises: 008_create_audit_logs
Create Date: 2026-01-01 00:00:08

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "009_create_prediction_items"
down_revision: Union[str, None] = "008_create_audit_logs"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_risk_level = sa.Enum(
    "unknown",
    "low",
    "moderate",
    "high",
    name="risk_level",
    native_enum=False,
    length=16,
)


def upgrade() -> None:
    op.create_table(
        "prediction_items",
        sa.Column(
            "id",
            sa.Uuid(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("prediction_id", sa.Uuid(), nullable=False),
        sa.Column("condition_code", sa.String(length=64), nullable=False),
        sa.Column("condition_label", sa.String(length=128), nullable=True),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("threshold", sa.Float(), nullable=True),
        sa.Column("risk_level", _risk_level, nullable=True),
        sa.Column("rank", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["prediction_id"],
            ["predictions.id"],
            name="fk_prediction_items_prediction_id_predictions",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_prediction_items"),
    )
    op.create_index(
        "ix_prediction_items_prediction_id",
        "prediction_items",
        ["prediction_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_prediction_items_prediction_id", table_name="prediction_items"
    )
    op.drop_table("prediction_items")
    bind = op.get_bind()
    _risk_level.drop(bind, checkfirst=True)
