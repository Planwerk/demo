---
title: Backend Scaffold
quadrant: reference
---

# Backend Scaffold

The backend scaffold provides the FastAPI application instance, configuration management,
async database connectivity, and the health check endpoint. All subsequent features build
on top of these modules.

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app, CORS middleware, API router
│   ├── config.py        # Settings class (pydantic-settings)
│   ├── database.py      # Async SQLAlchemy engine, session factory, Base
│   ├── models/          # ORM models (empty in scaffold)
│   ├── schemas/         # Pydantic schemas (empty in scaffold)
│   ├── api/
│   │   ├── routes/      # Route handlers (empty in scaffold)
│   │   └── __init__.py
│   └── services/        # Business logic (empty in scaffold)
├── tests/
│   ├── conftest.py      # Shared fixtures (sets JWT_SECRET before app import)
│   ├── unit/
│   └── integration/
├── pyproject.toml
└── .github/workflows/ci.yml
```

## Configuration (`app/config.py`)

The `Settings` class uses `pydantic-settings` `BaseSettings` to load and validate
environment variables at import time. It supports `.env` files via `env_file=".env"`.

A module-level `settings` instance is exported for use throughout the application.

### Environment Variables

| Variable                    | Type         | Default                                                    | Required | Description                                |
| --------------------------- | ------------ | ---------------------------------------------------------- | -------- | ------------------------------------------ |
| `DATABASE_URL`              | `str`        | `postgresql+asyncpg://user:pass@localhost:5432/statusboard`| No       | PostgreSQL connection string (asyncpg)     |
| `JWT_SECRET`                | `str`        | —                                                          | Yes      | Secret key for JWT signing                 |
| `JWT_ACCESS_EXPIRE_MINUTES` | `int`        | `30`                                                       | No       | Access token expiry in minutes             |
| `JWT_REFRESH_EXPIRE_DAYS`   | `int`        | `7`                                                        | No       | Refresh token expiry in days               |
| `CORS_ORIGINS`              | `str`        | `http://localhost:3000`                                    | No       | Comma-separated allowed CORS origins       |
| `WS_INITIAL_HOURS`          | `int`        | `1`                                                        | No       | Hours of history sent on WebSocket connect |
| `GITHUB_TOKEN`              | `str | None` | `None`                                                     | No       | GitHub PAT for issue/PR metadata           |
| `LOG_LEVEL`                 | `str`        | `INFO`                                                     | No       | Logging level (DEBUG, INFO, WARNING, ERROR)|

### Properties

| Property            | Return Type  | Description                                            |
| ------------------- | ------------ | ------------------------------------------------------ |
| `cors_origins_list` | `list[str]`  | Splits `CORS_ORIGINS` by comma and strips whitespace   |

### Imports

```python
from app.config import settings
```

## Database (`app/database.py`)

Async SQLAlchemy engine and session factory configured from `DATABASE_URL`.

### Exports

| Name                | Type                              | Description                                                  |
| ------------------- | --------------------------------- | ------------------------------------------------------------ |
| `async_engine`      | `AsyncEngine`                     | Async engine created with `create_async_engine`, echo=False  |
| `AsyncSessionLocal` | `async_sessionmaker[AsyncSession]`| Session factory bound to `async_engine`, expire_on_commit=False |
| `Base`              | `DeclarativeBase` subclass        | Base class for all ORM models                                |
| `get_db()`          | `AsyncGenerator[AsyncSession]`    | FastAPI dependency yielding an async session                 |

### `get_db()`

Async generator for use as a FastAPI dependency. Uses `async with AsyncSessionLocal()` to
ensure the session is closed after the request completes, including on exceptions.

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

@router.get("/example")
async def example(db: AsyncSession = Depends(get_db)):
    ...
```

### Imports

```python
from app.database import async_engine, AsyncSessionLocal, Base, get_db
```

## Health Check Endpoint

| Method | Path             | Auth     | Response        |
| ------ | ---------------- | -------- | --------------- |
| GET    | `/api/v1/health` | None     | `200 OK`        |

### Response Body

```json
{
  "status": "ok"
}
```

The health check has no database dependency and responds immediately.

## CORS Middleware

CORSMiddleware is configured on the FastAPI app with:

| Parameter           | Value                          |
| ------------------- | ------------------------------ |
| `allow_origins`     | `settings.cors_origins_list`   |
| `allow_credentials` | `True`                         |
| `allow_methods`     | `["*"]`                        |
| `allow_headers`     | `["*"]`                        |

## API Router

All API routes use the prefix `/api/v1`. The router is defined in `app/main.py` and
included in the FastAPI app instance.

```python
from app.main import app, router
```

## Tooling Configuration

### Ruff (`pyproject.toml`)

| Setting          | Value                                          |
| ---------------- | ---------------------------------------------- |
| `target-version` | `py313`                                        |
| `line-length`    | `99`                                           |
| `select`         | `E, F, W, I, N, UP, B, A, S, T20, SIM, TCH`   |
| `ignore`         | `S101` (assert in tests)                       |
| `isort`          | `known-first-party = ["app"]`                  |

### Pytest (`pyproject.toml`)

| Setting          | Value               |
| ---------------- | ------------------- |
| `asyncio_mode`   | `auto`              |
| `testpaths`      | `["tests"]`         |
| `addopts`        | `-v --tb=short`     |

### Mypy (`pyproject.toml`)

| Setting          | Value               |
| ---------------- | ------------------- |
| `python_version` | `3.13`              |
| `strict`         | `true`              |
| `plugins`        | `pydantic.mypy`     |

## CI Pipeline (`.github/workflows/ci.yml`)

Triggers on push to `main` and all pull requests.

| Job             | Runner          | Steps                                              |
| --------------- | --------------- | -------------------------------------------------- |
| `lint`          | `ubuntu-latest` | Checkout, setup uv + Python 3.13, `ruff check .`  |
| `test-backend`  | `ubuntu-latest` | Checkout, setup uv + Python 3.13, PostgreSQL 17 service, `pytest --tb=short -q` |

The `test-backend` job provisions a PostgreSQL 17 service container with
`DATABASE_URL=postgresql+asyncpg://test:test@localhost:5432/test_db` and
`JWT_SECRET=ci-test-secret`.
