---
title: Backend Scaffold
quadrant: reference
---

# Backend Scaffold

The backend scaffold provides the foundational project structure, configuration management, database connectivity, and health check endpoint upon which all subsequent features are built.

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application, CORS middleware, API router
│   ├── config.py         # Settings class (pydantic-settings)
│   ├── database.py       # Async SQLAlchemy engine, session factory, Base
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── health.py   # GET /api/v1/health endpoint
│   ├── models/
│   │   └── __init__.py
│   ├── schemas/
│   │   └── __init__.py
│   └── services/
│       └── __init__.py
├── tests/
│   ├── conftest.py
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_config.py
│   │   ├── test_database.py
│   │   └── test_health.py
│   └── integration/
│       └── __init__.py
└── pyproject.toml
```

## Environment Variables

All configuration is managed by the `Settings` class in `app/config.py`, which uses `pydantic-settings` `BaseSettings` with `.env` file support. Environment variables take precedence over `.env` values.

| Variable                    | Type         | Default                                                      | Required | Description                              |
| --------------------------- | ------------ | ------------------------------------------------------------ | -------- | ---------------------------------------- |
| `DATABASE_URL`              | `str`        | `postgresql+asyncpg://user:pass@localhost:5432/statusboard`  | No       | PostgreSQL connection string (asyncpg)   |
| `JWT_SECRET`                | `str`        | —                                                            | Yes      | Secret key for JWT signing               |
| `JWT_ACCESS_EXPIRE_MINUTES` | `int`        | `30`                                                         | No       | Access token expiry in minutes           |
| `JWT_REFRESH_EXPIRE_DAYS`   | `int`        | `7`                                                          | No       | Refresh token expiry in days             |
| `CORS_ORIGINS`              | `str`        | `http://localhost:3000`                                      | No       | Comma-separated allowed CORS origins     |
| `WS_INITIAL_HOURS`          | `int`        | `1`                                                          | No       | Hours of history sent on WebSocket connect|
| `GITHUB_TOKEN`              | `str | None` | `None`                                                       | No       | GitHub PAT for issue/PR metadata enrichment |
| `LOG_LEVEL`                 | `str`        | `INFO`                                                       | No       | Logging level (DEBUG, INFO, WARNING, ERROR) |

Missing `JWT_SECRET` raises a `pydantic.ValidationError` at import time.

### Settings Properties

| Property            | Return Type  | Description                                      |
| ------------------- | ------------ | ------------------------------------------------ |
| `cors_origins_list` | `list[str]`  | `CORS_ORIGINS` split by comma with whitespace trimmed |

### Usage

```python
from app.config import settings

settings.DATABASE_URL        # str
settings.cors_origins_list   # list[str]
```

## Database Module

`app/database.py` exports the async database layer. All exports use SQLAlchemy 2.0 APIs.

| Export              | Type                              | Description                                         |
| ------------------- | --------------------------------- | --------------------------------------------------- |
| `async_engine`      | `AsyncEngine`                     | Async engine created from `DATABASE_URL` (echo off) |
| `AsyncSessionLocal` | `async_sessionmaker[AsyncSession]` | Session factory bound to `async_engine`, `expire_on_commit=False` |
| `Base`              | `DeclarativeBase` subclass        | Base class for ORM model inheritance                |
| `get_db`            | `AsyncGenerator[AsyncSession]`    | FastAPI dependency yielding a session with guaranteed cleanup |

### `get_db()`

Async generator for FastAPI dependency injection. Uses `async with AsyncSessionLocal()` to guarantee session closure after each request, including on exceptions.

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

@router.get("/example")
async def example(db: AsyncSession = Depends(get_db)):
    ...
```

### `Base`

All ORM models inherit from `Base`:

```python
from app.database import Base

class MyModel(Base):
    __tablename__ = "my_table"
    ...
```

## Health Check Endpoint

| Method | Path             | Auth     | Response         |
| ------ | ---------------- | -------- | ---------------- |
| `GET`  | `/api/v1/health` | None     | `200 OK`         |

Response body:

```json
{"status": "ok"}
```

The health check has no database dependency and responds independently of database availability.

## CORS Middleware

CORS is configured on the FastAPI app with:

| Parameter           | Value                              |
| ------------------- | ---------------------------------- |
| `allow_origins`     | `settings.cors_origins_list`       |
| `allow_credentials` | `True`                             |
| `allow_methods`     | `["*"]`                            |
| `allow_headers`     | `["*"]`                            |

## API Router

All API endpoints are mounted under the prefix `/api/v1` via an `APIRouter`. The router is defined in `app/api/routes/health.py` and included on the `FastAPI` app instance in `app/main.py`.

## Tooling

| Tool    | Command                       | Configuration                                    |
| ------- | ----------------------------- | ------------------------------------------------ |
| Ruff    | `uv run ruff check .`        | `target-version='py313'`, select `E,F,I,UP,B,SIM` |
| Pytest  | `uv run pytest`              | `asyncio_mode='auto'`, `testpaths=['tests']`     |

## CI Pipeline

`.github/workflows/ci.yml` runs on push to `main` and on pull requests.

| Job            | Steps                                                        |
| -------------- | ------------------------------------------------------------ |
| `lint`         | Install uv, `uv run ruff check .` (Python 3.13)             |
| `test-backend` | PostgreSQL 17 service container, install uv, `uv run pytest --tb=short -q` (Python 3.13) |
