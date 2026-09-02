from fastapi import APIRouter, Depends, status

from app.auth.dependencies import get_user
from app.auth.models import User
from app.cart.schemas.add import CartAddRequest, CartAddResponse
from app.cart.services.add import cart_add
from app.cart.services.delete import cart_delete
from app.core.database import DbSession

router = APIRouter(prefix="/cart", tags=["cart"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=CartAddResponse)
async def cart_add_router(db: DbSession, request: CartAddRequest, user: User = Depends(get_user)) -> CartAddResponse:
    return await cart_add(db, request.option_id, user.id, request.quantity)


@router.delete("/{option_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cart_delete_router(option_id: str, user: User = Depends(get_user)) -> None:
    return await cart_delete(option_id, user.id)
