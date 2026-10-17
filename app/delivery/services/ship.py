from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.delivery.models import Delivery, DeliveryStatus
from app.delivery.schemas.ship import DeliveryShipRequest
from app.delivery.services.read import get_delivery_with_order_status
from app.order.models import Status


async def ship_delivery(
    db: AsyncSession,
    request: DeliveryShipRequest,
    delivery_id: str,
) -> Delivery:
    delivery, order_status = await get_delivery_with_order_status(db, delivery_id)
    if delivery.status != DeliveryStatus.PREPARING:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="해당 배송은 이미 발송 처리된 배송입니다.")

    if order_status != Status.PAID:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="해당 주문은 결제완료된 주문이 아닙니다.")

    delivery.courier = request.courier
    delivery.tracking_number = request.tracking_number
    delivery.status = DeliveryStatus.SHIPPING
    delivery.shipped_at = datetime.now(timezone.utc)

    await db.commit()
    return delivery
