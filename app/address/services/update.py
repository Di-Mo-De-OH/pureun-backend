from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.address.models import Address
from app.address.schemas.update import AddressUpdateRequest


async def update_address(db: AsyncSession, address_id: str, user_id: str, request: AddressUpdateRequest) -> Address:
    stmt = select(Address).where(Address.id == address_id, Address.user_id == user_id)
    result = await db.execute(stmt)
    address = result.scalar_one_or_none()
    if not address:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="해당 주소지를 찾을 수 없습니다.")

    if request.is_default and not address.is_default:
        old_default_address_stmt = select(Address).where(Address.user_id == user_id, Address.is_default.is_(True))
        old_default_address_result = await db.execute(old_default_address_stmt)
        old_default_address = old_default_address_result.scalar_one_or_none()
        if old_default_address:
            old_default_address.is_default = False
        address.is_default = request.is_default

    address.recipient_name = request.recipient_name
    address.phone_number = request.phone_number
    address.post_code = request.post_code
    address.base_address = request.base_address
    address.detail_address = request.detail_address

    await db.commit()

    return address
