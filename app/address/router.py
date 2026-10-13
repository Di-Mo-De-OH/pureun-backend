from collections.abc import Sequence

from fastapi import APIRouter, Depends, status

from app.address.models import Address
from app.address.schemas.create import AddressCreateRequest, AddressCreateResponse
from app.address.schemas.read import AddressReadResponse
from app.address.services.create import create_address
from app.address.services.delete import delete_address
from app.address.services.read import read_addresses
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


@router.get("", response_model=list[AddressReadResponse], status_code=status.HTTP_200_OK)
async def read_addresses_router(
    db: DbSession,
    user: User = Depends(get_user),
) -> Sequence[Address]:
    return await read_addresses(db, user.id)


@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_address_router(
    db: DbSession,
    address_id: str,
    user: User = Depends(get_user),
) -> None:
    await delete_address(db, address_id, user.id)
