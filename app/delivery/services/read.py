from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.delivery.models import Delivery
from app.order.models import Order, Status


async def get_delivery_with_order_status(db: AsyncSession, delivery_id: str) -> tuple[Delivery, Status]:
    delivery_stmt = select(Delivery).where(Delivery.id == delivery_id)
    delivery_result = await db.execute(delivery_stmt)
    delivery = delivery_result.scalar_one_or_none()
    if not delivery:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="해당 배송 정보를 찾을 수 없습니다.")
    order_stmt = select(Order).where(Order.id == delivery.order_id)
    order_result = await db.execute(order_stmt)
    order = order_result.scalar_one()

    return delivery, order.status
