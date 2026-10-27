from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.core.utils.validators import TrackingNumberField
from app.delivery.models import Courier, DeliveryStatus


class DeliveryShipRequest(BaseModel):
    courier: Courier
    tracking_number: TrackingNumberField


class DeliveryShipResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    status: DeliveryStatus
    shipped_at: datetime
