"""create predictions

Revision ID: 004_create_predictions
Revises: 007_create_consents
Create Date: 2026-01-01 00:00:05

Note: the revision chain is ordered by foreign-key dependency. See
migrations/README.md.
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "004_create_predictions"
down_revision: Union[str, None] = "007_create_consents"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_prediction_status = sa.Enum(
    "success",
    "low_quality",
    "uncertain",
    "abstained",
    "failed",
    name="prediction_status",
    native_enum=False,
    length=16,
)
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
        "predictions",
        sa.Column(
            "id",
            sa.Uuid(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("patient_id", sa.Uuid(), nullable=False),
        sa.Column("eye_image_id", sa.Uuid(), nullable=True),
        sa.Column("model_version_id", sa.Uuid(), nullable=True),
        sa.Column("consent_id", sa.Uuid(), nullable=True),
        sa.Column("requested_by_user_id", sa.Uuid(), nullable=True),
        sa.Column("status", _prediction_status, nullable=False),
        sa.Column("outcome_label", sa.String(length=128), nullable=True),
        sa.Column("risk_level", _risk_level, nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("uncertainty", sa.Float(), nullable=True),
        sa.Column("quality_score", sa.Float(), nullable=True),
        sa.Column("model_version_label", sa.String(length=64), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("error_code", sa.String(length=64), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
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
            ["patient_id"],
            ["patients.id"],
            name="fk_predictions_patient_id_patients",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["eye_image_id"],
            ["eye_images.id"],
            name="fk_predictions_eye_image_id_eye_images",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["model_version_id"],
            ["model_versions.id"],
            name="fk_predictions_model_version_id_model_versions",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["consent_id"],
            ["consents.id"],
            name="fk_predictions_consent_id_consents",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["requested_by_user_id"],
            ["users.id"],
            name="fk_predictions_requested_by_user_id_users",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_predictions"),
    )
    op.create_index("ix_predictions_patient_id", "predictions", ["patient_id"])
    op.create_index("ix_predictions_eye_image_id", "predictions", ["eye_image_id"])
    op.create_index(
        "ix_predictions_model_version_id", "predictions", ["model_version_id"]
    )
    op.create_index("ix_predictions_status", "predictions", ["status"])


def downgrade() -> None:
    op.drop_index("ix_predictions_status", table_name="predictions")
    op.drop_index("ix_predictions_model_version_id", table_name="predictions")
    op.drop_index("ix_predictions_eye_image_id", table_name="predictions")
    op.drop_index("ix_predictions_patient_id", table_name="predictions")
    op.drop_table("predictions")
    bind = op.get_bind()
    _risk_level.drop(bind, checkfirst=True)
    _prediction_status.drop(bind, checkfirst=True)
