from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.address.models import Address
from app.address.schemas.create import AddressCreateRequest

MAX_ADDRESS_COUNT = 5


async def create_address(db: AsyncSession, user_id: str, request: AddressCreateRequest) -> Address:
    stmt = select(Address).where(Address.user_id == user_id)
    result = await db.execute(stmt)
    addresses = result.scalars().all()
    if len(addresses) >= MAX_ADDRESS_COUNT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"주소지는 {MAX_ADDRESS_COUNT}개가 최대값 입니다."
        )
    is_default = request.is_default or not addresses
    if is_default:
        for existing in addresses:
            existing.is_default = False

    address = Address(
        user_id=user_id,
        recipient_name=request.recipient_name,
        phone_number=request.phone_number,
        post_code=request.post_code,
        base_address=request.base_address,
        detail_address=request.detail_address,
        is_default=is_default,
    )
    db.add(address)
    await db.commit()

    return address
