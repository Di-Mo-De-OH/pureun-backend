from typing import Any

from fastapi import status

PRODUCT_CREATE_RESPONSES: dict[int | str, dict[str, Any]] = {
    status.HTTP_400_BAD_REQUEST: {
        "description": "상품 등록 실패 (DB 제약 위반 등)",
        "content": {"application/json": {"example": {"detail": "상품 등록에 실패했습니다."}}},
    },
    status.HTTP_401_UNAUTHORIZED: {
        "description": "인증 토큰 없음, 만료, 로그아웃되었거나 존재하지 않는 유저",
        "content": {"application/json": {"example": {"detail": "유효하지 않은 토큰입니다."}}},
    },
    status.HTTP_403_FORBIDDEN: {
        "description": "관리자 권한 없음",
        "content": {"application/json": {"example": {"detail": "관리자만 접근 가능합니다."}}},
    },
}
