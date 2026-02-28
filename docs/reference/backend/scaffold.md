---
title: Backend Scaffold Reference
quadrant: reference
---

# Backend Scaffold Reference

## Environment Variables

All environment variables are managed by `app.config.Settings` using `pydantic-settings`. Values can be set via environment variables or a `.env` file in the backend directory.

| Variable | Type | Default | Required | Description |
|---|---|---|---|---|
| `DATABASE_URL` | `str` | `postgresql+asyncpg://USER:PASSWORD@localhost:5432/statusboard` | No | Async PostgreSQL connection string (must use `asyncpg` driver) |
| `JWT_SECRET` | `str` | — | **Yes** | Secret key for signing JWT tokens |
| `JWT_ACCESS_EXPIRE_MINUTES` | `int` | `30` | No | Access token expiration in minutes |
| `JWT_REFRESH_EXPIRE_DAYS` | `int` | `7` | No | Refresh token expiration in days |
| `CORS_ORIGINS` | `str` | `http://localhost:3000` | No | Comma-separated list of allowed CORS origins |
| `WS_INITIAL_HOURS` | `int` | `1` | No | WebSocket initial state history window in hours |
| `GITHUB_TOKEN` | `str \| None` | `None` | No | GitHub API token for integrations |
| `LOG_LEVEL` | `str` | `INFO` | No | Python logging level |

Import the singleton instance:

```python
from app.config import settings
```

`settings.cors_origins_list` returns `CORS_ORIGINS` split by comma into `list[str]`.

Missing `JWT_SECRET` raises a `ValidationError` at import time.

## Database Module

Module: `app.database`

### `get_engine()`

Returns an `AsyncEngine` created lazily via `create_async_engine(settings.DATABASE_URL, echo=False)`. Uses the `asyncpg` driver.

### `get_session_factory()`

Returns an `async_sessionmaker[AsyncSession]` bound to the engine from `get_engine()`, with `expire_on_commit=False`. Created lazily on first call.

### `Base`

`DeclarativeBase` subclass. All ORM models must inherit from `Base`.

```python
from app.database import Base

class MyModel(Base):
    __tablename__ = "my_model"
    ...
```

### `get_db()`

Async generator yielding an `AsyncSession`. Use as a FastAPI dependency:

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

@router.get("/items")
async def list_items(db: AsyncSession = Depends(get_db)):
    ...
```

The session is automatically closed when the request completes (via `async with`).

## Health Check Endpoint

```
GET /api/v1/health
```

**Authentication:** None required.

**Response:** `200 OK`

```json
{"status": "ok"}
```

No database dependency — remains responsive even if the database is unavailable.

## Project Structure

```
backend/
├── pyproject.toml          # Dependencies, ruff, pytest config
├── uv.lock                 # Locked dependency versions
├── app/
│   ├── __init__.py
│   ├── config.py           # Settings (pydantic-settings)
│   ├── database.py         # Engine, session factory, Base, get_db
│   ├── main.py             # FastAPI app, CORS, router, health check
│   ├── api/
│   │   └── routes/         # Route modules (future)
│   ├── models/             # SQLAlchemy ORM models (future)
│   ├── schemas/            # Pydantic request/response schemas (future)
│   └── services/           # Business logic services (future)
└── tests/
    ├── conftest.py          # Shared fixtures
    ├── unit/                # Unit tests
    └── integration/         # Integration tests
```
