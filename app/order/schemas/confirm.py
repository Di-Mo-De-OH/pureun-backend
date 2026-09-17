from pydantic import BaseModel

from app.order.models import Status


class OrderConfirmRequest(BaseModel):
    payment_key: str
    amount: int


class OrderConfirmResponse(BaseModel):
    status: Status
