

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.address.schemas.create import AddressCreateRequest
from app.address.models import Address
from sqlalchemy import select
from fastapi import HTTPException,status



async def create_address(
        db:AsyncSession,
        user_id:str,
        request:AddressCreateRequest
)->Address:
    stmt = select(Address).where(Address.user_id == user_id)
    result = await db.execute(stmt)
    default_address = result.scalars().all()
    if len(default_address) >=5:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail="주소지는 5개가 최대값 입니다."
        )
    if not default_address:
        is_default = True
    else:
        is_default = False



    address = Address(
        user_id = user_id,
        recipient_name=request.recipient_name,
        phone_number=request.phone_number,
        post_code = request.post_code,
        base_address=request.base_address,
        detail_address=request.detail_address,
        is_default=is_default,
    )
    db.add(address)
    await db.commit()

    return address


