import httpx
from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils.security import get_toss_auth_header
from app.order.models import Order, OrderItem, Status
from app.order.schemas.confirm import OrderConfirmRequest, OrderConfirmResponse
from app.products.models import ProductOption


async def call_toss_confirm(payment_key: str, order_id: str, amount: int) -> httpx.Response:
    async with httpx.AsyncClient() as client:
        return await client.post(
            "https://api.tosspayments.com/v1/payments/confirm",
            headers={"Authorization": f"Basic {get_toss_auth_header()}"},
            json={"paymentKey": payment_key, "orderId": order_id, "amount": amount},
        )


async def order_confirm(
    db: AsyncSession, order_id: str, user_id: str, request: OrderConfirmRequest
) -> OrderConfirmResponse:
    stmt = select(Order).where(Order.id == order_id)
    result = await db.execute(stmt)
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="존재하지 않는 주문 입니다.")

    if order.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="다른 사람의 주문내역은 확인할 수 없습니다.")
    if order.status != Status.PENDING:
        return OrderConfirmResponse(status=order.status)

    if order.amount != request.amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="주문금액과 결제 금액이 맞지 않습니다.")
    try:
        response = await call_toss_confirm(request.payment_key, order.id, request.amount)
    except httpx.HTTPError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="일시적으로 서비스를 사용할 수 없습니다."
        )
    if not response.status_code == status.HTTP_200_OK:
        order.status = Status.FAILED

    else:
        order.status = Status.PAID
        order.payment_key = request.payment_key

        item_stmt = select(OrderItem).where(OrderItem.order_id == order_id)
        item_result = await db.execute(item_stmt)
        order_items = item_result.scalars().all()
        for item in order_items:
            await db.execute(
                update(ProductOption)
                .where(ProductOption.id == item.option_id)
                .values(stock=ProductOption.stock - item.quantity)
            )

    await db.commit()
    return OrderConfirmResponse(status=order.status)
