"""create consents

Revision ID: 007_create_consents
Revises: 006_create_model_versions
Create Date: 2026-01-01 00:00:04

Note: the revision chain is ordered by foreign-key dependency. See
migrations/README.md.
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "007_create_consents"
down_revision: Union[str, None] = "006_create_model_versions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_consent_type = sa.Enum(
    "screening", "storage", "research", name="consent_type", native_enum=False, length=32
)
_consent_status = sa.Enum(
    "pending",
    "granted",
    "withdrawn",
    "expired",
    name="consent_status",
    native_enum=False,
    length=32,
)


def upgrade() -> None:
    op.create_table(
        "consents",
        sa.Column(
            "id",
            sa.Uuid(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("patient_id", sa.Uuid(), nullable=False),
        sa.Column("consent_type", _consent_type, nullable=False),
        sa.Column("status", _consent_status, nullable=False),
        sa.Column("granted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("withdrawn_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("document_ref", sa.String(length=512), nullable=True),
        sa.Column("recorded_by_user_id", sa.Uuid(), nullable=True),
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
            name="fk_consents_patient_id_patients",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["recorded_by_user_id"],
            ["users.id"],
            name="fk_consents_recorded_by_user_id_users",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_consents"),
    )
    op.create_index("ix_consents_patient_id", "consents", ["patient_id"])
    op.create_index("ix_consents_status", "consents", ["status"])


def downgrade() -> None:
    op.drop_index("ix_consents_status", table_name="consents")
    op.drop_index("ix_consents_patient_id", table_name="consents")
    op.drop_table("consents")
    bind = op.get_bind()
    _consent_status.drop(bind, checkfirst=True)
    _consent_type.drop(bind, checkfirst=True)
