"""Reference-data seeding.

Seeds only non-clinical, non-sensitive reference data (RBAC roles). It is
idempotent and safe to run repeatedly.

This module intentionally does NOT create users, patients or any clinical
data. A bootstrap administrator must be provisioned explicitly from
deployment secrets; the required inputs are recorded in the Phase 2 report
rather than hard-coded here.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import DEFAULT_ROLES
from app.core.logging_config import get_logger
from app.database.session import session_scope

logger = get_logger(__name__)

_ROLE_DESCRIPTIONS = {
    "admin": "Full administrative access.",
    "clinician": "Clinical screening workflows and review.",
    "operator": "Image upload and screening execution.",
    "researcher": "Read-only access to aggregates and metadata.",
}


async def seed_roles(session: AsyncSession) -> int:
    """Insert any missing default roles. Returns the number created."""
    from app.models.role import Role

    result = await session.execute(select(Role.name))
    existing = {row[0] for row in result.all()}

    created = 0
    for role_name in DEFAULT_ROLES:
        if role_name in existing:
            continue
        session.add(
            Role(
                name=role_name,
                description=_ROLE_DESCRIPTIONS.get(role_name, ""),
                is_system=True,
            )
        )
        created += 1

    if created:
        await session.flush()
        logger.info("seeded_roles", extra={"created": created})
    return created


async def seed_reference_data(session: AsyncSession) -> dict[str, int]:
    """Seed all reference data. Returns a per-entity creation summary."""
    roles_created = await seed_roles(session)
    return {"roles_created": roles_created}


async def run_seed() -> dict[str, int]:
    """Entry point for ``python -m app.database.seed``."""
    async with session_scope() as session:
        return await seed_reference_data(session)


if __name__ == "__main__":  # pragma: no cover - manual invocation only
    import asyncio

    print(asyncio.run(run_seed()))
