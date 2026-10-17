from sqlalchemy.ext.asyncio import AsyncSession

from app.address.models import Address
from app.delivery.models import Delivery


def create_delivery(db: AsyncSession, order_id: str, address: Address) -> None:

    delivery = Delivery(
        order_id=order_id,
        recipient_name=address.recipient_name,
        phone_number=address.phone_number,
        post_code=address.post_code,
        base_address=address.base_address,
        detail_address=address.detail_address,
    )
    db.add(delivery)
