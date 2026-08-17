from fastapi import APIRouter, Depends, status

from app.auth.dependencies import get_admin_user
from app.auth.models import User
from app.core.database import DbSession
from app.products.models import Product
from app.products.schemas.create import ProductCreateRequest, ProductCreateResponse
from app.products.services.create import create_product
from app.products.utils.responses import PRODUCT_CREATE_RESPONSES

router = APIRouter(prefix="/products", tags=["products"])


@router.post(
    "", status_code=status.HTTP_201_CREATED, response_model=ProductCreateResponse, responses=PRODUCT_CREATE_RESPONSES
)
async def create_product_router(
    db: DbSession,
    request: ProductCreateRequest,
    admin: User = Depends(get_admin_user),
) -> Product:
    return await create_product(db, request)
