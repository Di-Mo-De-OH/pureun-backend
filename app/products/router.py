from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.auth.dependencies import get_admin_user
from app.auth.models import User
from app.core.database import DbSession
from app.core.s3 import PresignedUrlRequest, PresignedUrlResponse, create_presigned_upload_url
from app.core.utils.pagination import CursorPage, CursorPageParams
from app.products.models import Product
from app.products.schemas.create import ProductCreateRequest, ProductCreateResponse
from app.products.schemas.read import ProductDetailResponse, ProductSummaryResponse
from app.products.schemas.update import ProductUpdateRequest, ProductUpdateResponse
from app.products.services.create import create_product
from app.products.services.read import get_product_detail, get_products
from app.products.services.update import update_product
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


@router.post("/images/presigned-url", status_code=status.HTTP_200_OK, response_model=PresignedUrlResponse)
async def create_product_image_presigned_url_router(
    request: PresignedUrlRequest,
    admin_user: User = Depends(get_admin_user),
) -> PresignedUrlResponse:
    return create_presigned_upload_url(request, prefix="products")


@router.get("", status_code=status.HTTP_200_OK, response_model=CursorPage[ProductSummaryResponse])
async def read_products_router(
    db: DbSession, params: Annotated[CursorPageParams, Depends()]
) -> CursorPage[ProductSummaryResponse]:
    return await get_products(db, params)


@router.get("/{product_id}", status_code=status.HTTP_200_OK, response_model=ProductDetailResponse)
async def read_product_router(db: DbSession, product_id: str) -> Product:
    return await get_product_detail(db, product_id)


@router.put("/{product_id}", status_code=status.HTTP_200_OK, response_model=ProductUpdateResponse)
async def update_product_router(
    db: DbSession, product_id: str, request: ProductUpdateRequest, admin_user: User = Depends(get_admin_user)
) -> Product:
    return await update_product(db, product_id, request)
