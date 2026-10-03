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
        # 요청 받은 데이터의 id 를 뽑는 과정
        for img in product.images:
            # db값을 img 에 담는 for문
            if img.id not in request_image_ids:
                # db에서 꺼내온 id 값이 요청으로 들어온 id 값에 없다면
                await db.delete(img)
                # 해당 로우 삭제

        existing_img_ids = {img.id: img for img in product.images}
        # id 값을 키로 ProductImage 객체를 가져옴 ex) {"img_id":ProductImage객체}
        for sort_order, img_data in enumerate(request.images):
            # 요청받은 데이터를 img_data에 담는 과정
            if img_data.id is not None and img_data.id in existing_img_ids:
                # 해당 데이터의 id값이 있고 db에 존재한다면
                existing_img = existing_img_ids[img_data.id]
                # id로 딕셔너리에서 실제 ProductImage 객체를 꺼내옴
                # (딕셔너리 아님,객체라서 .필드명으로 접근가능 즉 속성으로 접근가능)
                existing_img.image_key = img_data.image_key
                # 실제 데이터를 요청받은 데이터로 덮음
                existing_img.sort_order = sort_order
                # 실제 데이터를 요청받은 데이터로 덮음

            else:
                db.add(
                    ProductImage(product_id=product.id, sort_order=sort_order, **img_data.model_dump(exclude={"id"}))
                )
                # 만약 요청받은 id값이 db에 존재하지 않는다면 새로운 로우로 데이터를 만듦

        label_data = request.label.model_dump()
        for field, value in label_data.items():
            setattr(product.label, field, value)

        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="상품 수정에 실패했습니다.")
    await db.refresh(product)
    return product
