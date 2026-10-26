from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.delivery.models import Delivery, DeliveryStatus
from app.delivery.services.read import get_delivery_with_order_status


async def complete_delivery(
    db: AsyncSession,
    delivery_id: str,
) -> Delivery:
    delivery, _ = await get_delivery_with_order_status(db, delivery_id)
    if delivery.status == DeliveryStatus.DELIVERED:
        return delivery
    if delivery.status != DeliveryStatus.SHIPPING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="배송중인 건만 배송완료 처리할 수 있습니다."
        )
    delivery.status = DeliveryStatus.DELIVERED
    delivery.delivered_at = datetime.now(timezone.utc)

    await db.commit()
    return delivery
