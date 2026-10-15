"""create model_versions

Revision ID: 006_create_model_versions
Revises: 003_create_eye_images
Create Date: 2026-01-01 00:00:03

Note: the revision chain is ordered by foreign-key dependency, which is not
the same as the file-number order. See migrations/README.md.
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "006_create_model_versions"
down_revision: Union[str, None] = "003_create_eye_images"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_model_status = sa.Enum(
    "candidate",
    "approved",
    "deprecated",
    "retired",
    name="model_status",
    native_enum=False,
    length=16,
)


def upgrade() -> None:
    op.create_table(
        "model_versions",
        sa.Column(
            "id",
            sa.Uuid(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("version", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("status", _model_status, nullable=False),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column("artifact_uri", sa.String(length=1024), nullable=True),
        sa.Column("checksum", sa.String(length=128), nullable=True),
        sa.Column("input_contract_version", sa.String(length=32), nullable=True),
        sa.Column("output_contract_version", sa.String(length=32), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("retired_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
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
        sa.PrimaryKeyConstraint("id", name="pk_model_versions"),
        sa.UniqueConstraint("version", name="uq_model_versions_version"),
    )
    op.create_index(
        "ix_model_versions_version", "model_versions", ["version"], unique=True
    )
    op.create_index(
        "ix_model_versions_status", "model_versions", ["status"], unique=False
    )
    op.create_index(
        "ix_model_versions_is_active",
        "model_versions",
        ["is_active"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_model_versions_is_active", table_name="model_versions")
    op.drop_index("ix_model_versions_status", table_name="model_versions")
    op.drop_index("ix_model_versions_version", table_name="model_versions")
    op.drop_table("model_versions")
    bind = op.get_bind()
    _model_status.drop(bind, checkfirst=True)
