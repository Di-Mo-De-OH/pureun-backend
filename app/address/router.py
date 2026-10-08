from fastapi import APIRouter, Depends, status

from app.address.models import Address
from app.address.schemas.create import AddressCreateRequest, AddressCreateResponse
from app.address.services.create import create_address
from app.auth.dependencies import get_user
from app.auth.models import User
from app.core.database import DbSession

router = APIRouter(
    prefix="/addresses",
    tags=["addresses"],
)


@router.post("", response_model=AddressCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_address_router(
    db: DbSession,
    request: AddressCreateRequest,
    user: User = Depends(get_user),
) -> Address:
    return await create_address(db, user.id, request)
