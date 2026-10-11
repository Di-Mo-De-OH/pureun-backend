from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.address.models import Address


async def read_addresses(db: AsyncSession, user_id: str) -> Sequence[Address]:
    stmt = (
        select(Address).where(Address.user_id == user_id).order_by(Address.is_default.desc(), Address.created_at.desc())
    )
    result = await db.execute(stmt)
    addresses = result.scalars().all()
    return addresses
