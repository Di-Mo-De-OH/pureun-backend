from collections.abc import Sequence

from fastapi import HTTPException, status
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


async def get_address(db: AsyncSession, address_id: str, user_id: str) -> Address:
    stmt = select(Address).where(Address.id == address_id, Address.user_id == user_id)
    result = await db.execute(stmt)
    address = result.scalar_one_or_none()
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="주소지를 찾을 수 없습니다.",
        )
    return address
