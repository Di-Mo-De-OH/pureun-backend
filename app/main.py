from fastapi import FastAPI

from app.address.router import router as address_router
from app.auth.router import router as auth_router
from app.cart.router import router as cart_router
from app.delivery.router import router as delivery_router
from app.order.router import router as order_router
from app.products.router import router as product_router

app = FastAPI()
app.include_router(auth_router, prefix="/api/v1")
app.include_router(product_router, prefix="/api/v1")
app.include_router(cart_router, prefix="/api/v1")
app.include_router(order_router, prefix="/api/v1")
app.include_router(address_router, prefix="/api/v1")
app.include_router(delivery_router, prefix="/api/v1")
