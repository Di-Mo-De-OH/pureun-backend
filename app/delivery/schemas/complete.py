from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.delivery.models import DeliveryStatus


class DeliveryCompleteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    status: DeliveryStatus
    delivered_at: datetime
