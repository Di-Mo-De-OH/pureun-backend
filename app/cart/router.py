from fastapi import APIRouter, Depends, status

from app.auth.dependencies import get_user
from app.auth.models import User
from app.cart.schemas.add import CartAddRequest, CartAddResponse
from app.cart.services.add import cart_add
from app.core.database import DbSession

router = APIRouter(prefix="/cart", tags=["cart"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=CartAddResponse)
async def cart_add_router(db: DbSession, request: CartAddRequest, user: User = Depends(get_user)) -> CartAddResponse:
    return await cart_add(db, request.option_id, user.id, request.quantity)
