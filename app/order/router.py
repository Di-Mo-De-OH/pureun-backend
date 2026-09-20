from fastapi import APIRouter, Depends, status

from app.auth.dependencies import get_user
from app.auth.models import User
from app.core.database import DbSession
from app.order.schemas.buy_now import OrderBuyNowRequest, OrderBuyNowResponse
from app.order.schemas.cart_checkout import OrderCartCheckoutRequest, OrderCartCheckoutResponse
from app.order.schemas.confirm import OrderConfirmRequest, OrderConfirmResponse
from app.order.services.buy_now import order_buy_now
from app.order.services.cart_checkout import cart_checkout
from app.order.services.confirm import order_confirm

router = APIRouter(
    prefix="/orders",
    tags=["Order"],
)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=OrderBuyNowResponse)
async def buy_now_router(
    db: DbSession, request: OrderBuyNowRequest, user: User = Depends(get_user)
) -> OrderBuyNowResponse:
    return await order_buy_now(db, user.id, request.option_id, request.quantity)


@router.post("/{order_id}/confirm", status_code=status.HTTP_200_OK, response_model=OrderConfirmResponse)
async def confirm_router(
    db: DbSession, request: OrderConfirmRequest, order_id: str, user: User = Depends(get_user)
) -> OrderConfirmResponse:
    return await order_confirm(db, order_id, user.id, request)


@router.post("/cart-checkout", status_code=status.HTTP_201_CREATED, response_model=OrderCartCheckoutResponse)
async def checkout_router(
    db: DbSession,
    request: OrderCartCheckoutRequest,
    user: User = Depends(get_user),
) -> OrderCartCheckoutResponse:
    return await cart_checkout(db, user.id, request)
