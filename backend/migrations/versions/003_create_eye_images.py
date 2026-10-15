"""create eye_images

Revision ID: 003_create_eye_images
Revises: 002_create_patients
Create Date: 2026-01-01 00:00:02

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003_create_eye_images"
down_revision: Union[str, None] = "002_create_patients"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_eye_side = sa.Enum(
    "left", "right", "unknown", name="eye_side", native_enum=False, length=16
)
_quality_status = sa.Enum(
    "unknown",
    "acceptable",
    "insufficient",
    name="quality_status",
    native_enum=False,
    length=16,
)


def upgrade() -> None:
    op.create_table(
        "eye_images",
        sa.Column(
            "id",
            sa.Uuid(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("patient_id", sa.Uuid(), nullable=False),
        sa.Column("eye_side", _eye_side, nullable=False),
        sa.Column("quality_status", _quality_status, nullable=False),
        sa.Column("storage_key", sa.String(length=512), nullable=False),
        sa.Column("media_type", sa.String(length=64), nullable=False),
        sa.Column("byte_size", sa.BigInteger(), nullable=True),
        sa.Column("width", sa.Integer(), nullable=True),
        sa.Column("height", sa.Integer(), nullable=True),
        sa.Column("checksum_sha256", sa.String(length=64), nullable=True),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("uploaded_by_user_id", sa.Uuid(), nullable=True),
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
            name="fk_eye_images_patient_id_patients",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["uploaded_by_user_id"],
            ["users.id"],
            name="fk_eye_images_uploaded_by_user_id_users",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_eye_images"),
    )
    op.create_index("ix_eye_images_patient_id", "eye_images", ["patient_id"])
    op.create_index(
        "ix_eye_images_quality_status", "eye_images", ["quality_status"]
    )
    op.create_index(
        "ix_eye_images_checksum_sha256", "eye_images", ["checksum_sha256"]
    )


def downgrade() -> None:
    op.drop_index("ix_eye_images_checksum_sha256", table_name="eye_images")
    op.drop_index("ix_eye_images_quality_status", table_name="eye_images")
    op.drop_index("ix_eye_images_patient_id", table_name="eye_images")
    op.drop_table("eye_images")
    bind = op.get_bind()
    _eye_side.drop(bind, checkfirst=True)
    _quality_status.drop(bind, checkfirst=True)
