from fastapi import APIRouter, Depends, status

from app.auth.dependencies import get_user
from app.auth.models import User
from app.core.database import DbSession
from app.order.schemas.buy_now import OrderBuyNowRequest, OrderBuyNowResponse
from app.order.services.buy_now import order_buy_now

router = APIRouter(
    prefix="/orders",
    tags=["Order"],
)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=OrderBuyNowResponse)
async def buy_now_router(
    db: DbSession, request: OrderBuyNowRequest, user: User = Depends(get_user)
) -> OrderBuyNowResponse:
    return await order_buy_now(db, user.id, request.option_id, request.quantity)
