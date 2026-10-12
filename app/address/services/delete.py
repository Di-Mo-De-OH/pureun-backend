from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.address.models import Address


async def delete_address(db: AsyncSession, address_id: str, user_id: str) -> None:
    stmt = select(Address).where(Address.user_id == user_id, Address.id == address_id)
    result = await db.execute(stmt)
    address = result.scalar_one_or_none()
    if not address:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="해당 주소지는 존재하지 않습니다.")
    await db.delete(address)
    if address.is_default:
        next_default_stmt = select(Address).where(Address.user_id == user_id).order_by(Address.created_at.desc())
        next_default_result = await db.execute(next_default_stmt)
        next_default_address = next_default_result.scalars().first()
        if next_default_address:
            next_default_address.is_default = True

    await db.commit()
