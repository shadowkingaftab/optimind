"""create reports

Revision ID: 005_create_reports
Revises: 004_create_predictions
Create Date: 2026-01-01 00:00:06

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "005_create_reports"
down_revision: Union[str, None] = "004_create_predictions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_report_status = sa.Enum(
    "pending",
    "generated",
    "failed",
    name="report_status",
    native_enum=False,
    length=16,
)


def upgrade() -> None:
    op.create_table(
        "reports",
        sa.Column(
            "id",
            sa.Uuid(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("patient_id", sa.Uuid(), nullable=False),
        sa.Column("prediction_id", sa.Uuid(), nullable=True),
        sa.Column("status", _report_status, nullable=False),
        sa.Column("storage_key", sa.String(length=512), nullable=True),
        sa.Column("media_type", sa.String(length=64), nullable=True),
        sa.Column("byte_size", sa.BigInteger(), nullable=True),
        sa.Column("checksum_sha256", sa.String(length=64), nullable=True),
        sa.Column("error_code", sa.String(length=64), nullable=True),
        sa.Column("generated_by_user_id", sa.Uuid(), nullable=True),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=True),
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
            name="fk_reports_patient_id_patients",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["prediction_id"],
            ["predictions.id"],
            name="fk_reports_prediction_id_predictions",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["generated_by_user_id"],
            ["users.id"],
            name="fk_reports_generated_by_user_id_users",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_reports"),
    )
    op.create_index("ix_reports_patient_id", "reports", ["patient_id"])
    op.create_index("ix_reports_prediction_id", "reports", ["prediction_id"])
    op.create_index("ix_reports_status", "reports", ["status"])


def downgrade() -> None:
    op.drop_index("ix_reports_status", table_name="reports")
    op.drop_index("ix_reports_prediction_id", table_name="reports")
    op.drop_index("ix_reports_patient_id", table_name="reports")
    op.drop_table("reports")
    bind = op.get_bind()
    _report_status.drop(bind, checkfirst=True)
