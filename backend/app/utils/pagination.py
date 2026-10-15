"""Pagination helpers for SQLAlchemy statements."""

from __future__ import annotations

from typing import Sequence, Tuple, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.pagination import PageParams

T = TypeVar("T")


async def paginate(
    session: AsyncSession,
    stmt: select,
    params: PageParams,
) -> Tuple[Sequence[T], int]:
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await session.execute(count_stmt)).scalar() or 0
    paged_stmt = stmt.offset(params.offset).limit(params.limit)
    result = await session.execute(paged_stmt)
    items = result.scalars().all()
    return items, int(total)


def apply_pagination(stmt: select, params: PageParams) -> select:
    return stmt.offset(params.offset).limit(params.limit)
