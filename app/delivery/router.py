from fastapi import APIRouter, Depends, status

from app.auth.dependencies import get_admin_user
from app.auth.models import User
from app.core.database import DbSession
from app.delivery.models import Delivery
from app.delivery.schemas.complete import DeliveryCompleteResponse
from app.delivery.schemas.ship import DeliveryShipRequest, DeliveryShipResponse
from app.delivery.services.complete import complete_delivery
from app.delivery.services.ship import ship_delivery

router = APIRouter(prefix="/deliveries", tags=["Delivery"])


@router.post("/{delivery_id}/ship", response_model=DeliveryShipResponse, status_code=status.HTTP_200_OK)
async def ship_delivery_router(
    db: DbSession,
    delivery_id: str,
    request: DeliveryShipRequest,
    admin_user: User = Depends(get_admin_user),
) -> Delivery:
    return await ship_delivery(db, request, delivery_id)


@router.post("/{delivery_id}/complete", response_model=DeliveryCompleteResponse, status_code=status.HTTP_200_OK)
async def complete_delivery_router(
    db: DbSession,
    delivery_id: str,
    admin_user: User = Depends(get_admin_user),
) -> Delivery:
    return await complete_delivery(db, delivery_id)
