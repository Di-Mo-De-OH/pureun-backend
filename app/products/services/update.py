from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.products.models import Product, ProductImage, ProductOption
from app.products.schemas.update import ProductUpdateRequest


async def update_product(db: AsyncSession, product_id: str, request: ProductUpdateRequest) -> Product:
    stmt = (
        select(Product)
        .where(Product.id == product_id)
        .options(selectinload(Product.options), selectinload(Product.images), selectinload(Product.label))
    )
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="해당 상품을 찾을 수 없습니다.")
    product.category = request.category
    product.name = request.name
    product.description = request.description
    product.is_active = request.is_active
    product.supplier_code = request.supplier_code

    try:
        request_option_ids = {opt.id for opt in request.options if opt.id is not None}
        for option in product.options:
            if option.id not in request_option_ids:
                await db.delete(option)

        existing_options = {opt.id: opt for opt in product.options}
        for option_data in request.options:
            if option_data.id is not None and option_data.id in existing_options:
                existing = existing_options[option_data.id]
                existing.option_name = option_data.option_name
                existing.price = option_data.price
                existing.discount_price = option_data.discount_price
                existing.stock = option_data.stock
            else:
                db.add(ProductOption(product_id=product.id, **option_data.model_dump(exclude={"id"})))

        request_image_ids = {img.id for img in request.images if img.id is not None}
        for img in product.images:
            if img.id not in request_image_ids:
                await db.delete(img)

        existing_img_ids = {img.id: img for img in product.images}
        for img_data in request.images:
            if img_data.id is not None and img_data.id in existing_img_ids:
                existing_img = existing_img_ids[img_data.id]
                existing_img.image_key = img_data.image_key
                existing_img.sort_order = img_data.sort_order

            else:
                db.add(ProductImage(product_id=product.id, **img_data.model_dump(exclude={"id"})))

        label_data = request.label.model_dump()
        for field, value in label_data.items():
            setattr(product.label, field, value)

        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="상품 수정에 실패했습니다.")
    await db.refresh(product)
    return product
