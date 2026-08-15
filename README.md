# pureun

FastAPI 기반 식료품 판매 플랫폼 백엔드 API 서버

> `vintage-house-reborn`(빈티지 의류 쇼핑몰) 프로젝트의 방향을 식료품 판매 플랫폼으로 전환하면서 새로 시작한 레포입니다.
> auth + 공용 인프라(JWT 인증, 이메일 인증, S3 업로드, DB/Redis 연결)는 기존 프로젝트에서 그대로 가져왔고,
> products/cart/payments/delivery는 식료품 도메인에 맞춰 새로 설계합니다.

## 프로젝트 목표

포트폴리오용 데모가 아니라 **실제 서비스로 운영하는 것**을 목표로 합니다. 유저 인증부터 상품 등록, 장바구니,
결제, 배송까지 구매 흐름 전체를 갖춘 식료품 판매 플랫폼을 만듭니다.

**로드맵**

1. **유저** — 회원가입/로그인/내 정보 관리 (완료)
2. **상품** — 상품 등록/조회/수정/삭제 CRUD (다음 단계)
3. **장바구니** — 상품 담기/수량 관리/조회
4. **결제** — 주문 생성 및 결제 연동
5. **배송** — 배송지 관리, 배송 상태 추적

## 기술 스택

- **Framework**: FastAPI (Python 3.13)
- **Database**: PostgreSQL
- **Cache**: Redis
- **ORM**: SQLAlchemy (async) + Alembic
- **패키지 관리**: uv
- **Infra**: Docker, Docker Compose, AWS EC2

## 현재 상태

**1. 유저**
- [x] 이메일 인증 기반 회원가입
- [x] 로그인 / 로그아웃 (JWT 액세스 토큰 + 리프레시 토큰, 로그아웃 시 액세스 토큰 블랙리스트)
- [x] 리프레시 토큰으로 액세스 토큰 재발급
- [x] 내 정보 조회 / 수정 / 회원 탈퇴 (`/me`)
- [x] 관리자 권한 구분 (`User.is_admin`)

**2. 상품**
- [ ] 상품 모델 설계 (카테고리, 재고 수량)
- [ ] 상품 등록 / 조회 / 수정 / 삭제 CRUD
- [ ] 상품 이미지 업로드 (S3 presigned URL)

**3. 장바구니**
- [ ] 담기 / 수량 변경 / 삭제
- [ ] 조회

**4. 결제**
- [ ] 주문 생성
- [ ] 결제 연동

**5. 배송**
- [ ] 배송지 관리
- [ ] 배송 상태 추적

## API 엔드포인트

**인증** (`/api/v1/auth`)
```
POST    /api/v1/auth/send-email
POST    /api/v1/auth/verify-email
POST    /api/v1/auth/signup
POST    /api/v1/auth/login
POST    /api/v1/auth/logout
POST    /api/v1/auth/refresh
GET     /api/v1/auth/me
PATCH   /api/v1/auth/me
DELETE  /api/v1/auth/me
```

전체 요청/응답 스펙은 `/docs`(Swagger UI)에서 확인 가능합니다.

## 프로젝트 구조

```
app/
├── auth/                # 회원가입, 로그인/로그아웃, 토큰 재발급, 내 정보(/me), 이메일 인증
│   ├── router.py        # 엔드포인트 (라우팅 배선만)
│   ├── models.py        # User(is_admin 포함), RefreshToken
│   ├── dependencies.py  # 인증/권한 의존성 (get_user_id/get_user/get_admin_user), 다른 앱에서도 재사용
│   ├── schemas/         # 요청/응답 Pydantic 스키마 (기능별 분리: email.py, signup.py, me.py 등)
│   ├── services/        # 비즈니스 로직 (기능별 분리: email.py, signup.py, me.py 등)
│   └── utils/
│       ├── redis.py     # Redis 키 네이밍 (EmailRedis, LogoutRedis)
│       └── responses.py # 엔드포인트별 OpenAPI 에러 응답 문서
├── core/                # 공용 기술
│   ├── config.py        # 환경변수 설정 (pydantic-settings)
│   ├── database.py       # SQLAlchemy async engine/session, BaseModel(ULID PK)
│   ├── redis.py          # Redis 비동기 클라이언트
│   ├── s3.py              # S3 presigned URL 발급/삭제
│   └── utils/
│       ├── email.py       # SMTP 이메일 발송
│       ├── pagination.py  # 커서 기반 페이지네이션
│       ├── security.py    # OTP/토큰 생성, 비밀번호 해싱 함수
│       └── validators.py  # 재사용 가능한 Pydantic 검증 타입 (EmailField 등)
└── main.py
```

products/cart/payments/delivery 앱은 로드맵 순서대로 이 자리에 추가됩니다.

## 브랜치 전략

```
main        ← 실서버 배포
  └── develop    ← 로컬 테스트
        └── feature/*  ← 기능 개발
```

## 시작하기

**환경변수 설정**

```bash
cp env/example.env env/.env
# env/.env 파일에 실제 값 입력
```

필요한 환경변수 목록은 `env/example.env` 참고. `DATABASE_URL`/`REDIS_URL`은 직접 입력하지 않고, `POSTGRES_*`/`REDIS_*` 값들을 조합해서 `app/core/config.py`가 자동으로 만들어줌 (비밀번호 중복 저장으로 인한 불일치 방지).

**서버 실행**

```bash
docker compose up --build
```

로컬 서버: `http://localhost:8001`

API 문서: `http://localhost:8001/docs`

## DB 마이그레이션 (Alembic)

```bash
# 모델 변경 감지 후 마이그레이션 파일 생성
docker compose exec fastapi uv run alembic revision --autogenerate -m "메시지"

# 마이그레이션 적용
docker compose exec fastapi uv run alembic upgrade head
```

새 앱에 모델을 추가하면 `alembic/env.py`에도 `import app.{app_name}.models`를 추가해야 alembic이 인식함.

## 데이터베이스 스키마

모든 모델은 공통으로 `id`(ULID, 26자), `created_at`, `updated_at`를 가짐 (`app/core/database.py`의 `BaseModel`).

| 테이블 | 설명 |
|---|---|
| `users` | 회원 정보 (email, nickname, address, is_admin 등) |
| `refresh_tokens` | JWT Refresh Token 저장 (해시값만 저장) |

## 개발 명령어

```bash
make format   # 코드 포맷 (black, ruff)
make type     # 타입 검사 (mypy)
make check    # 전체 검사 (format + type + test)
```

## CI/CD

| 워크플로우 | 트리거 | 역할 |
|-----------|--------|------|
| CI | develop, main PR | lint + test 자동 검사 + Discord 알림 |
| CD | main push | 빌드 → Docker Hub → EC2 자동 배포 + Discord 알림 |

- **API 문서(운영)**: https://api.ohdimode.com/docs
- HTTPS(Let's Encrypt) + nginx 리버스 프록시, AWS EC2(Elastic IP 고정) 배포

`vintage-house-reborn` 프로젝트를 폐기하고 같은 EC2 서버/도메인(`api.ohdimode.com`)을 이어받아 운영합니다.
