---
title: Backend Scaffold
quadrant: backend
---

# Backend Scaffold

Project scaffold for the FastAPI backend: configuration, database layer, and application entry point.

## Directory Structure

```
backend/
  pyproject.toml          # Project metadata, dependencies, tool config
  app/
    __init__.py
    config.py             # Settings class (pydantic-settings)
    database.py           # Async engine, session factory, Base, get_db()
    main.py               # FastAPI app, CORS, health check
    models/               # ORM models (future)
    schemas/              # Pydantic request/response schemas (future)
    api/
      routes/             # Route modules (future)
    services/             # Business logic (future)
  tests/
    conftest.py           # Shared fixtures (test_settings, client)
    unit/                 # Unit tests
    integration/          # Integration tests (future)
```

## Configuration (`app/config.py`)

`Settings` extends `pydantic_settings.BaseSettings` and loads values from environment variables and `.env` files.

### Environment Variables

| Variable | Type | Default | Required |
|---|---|---|---|
| `DATABASE_URL` | `str` | `postgresql+asyncpg://user:pass@localhost:5432/statusboard` | No |
| `JWT_SECRET` | `str` | *none* | **Yes** |
| `JWT_ACCESS_EXPIRE_MINUTES` | `int` | `30` | No |
| `JWT_REFRESH_EXPIRE_DAYS` | `int` | `7` | No |
| `CORS_ORIGINS` | `list[str]` | `["http://localhost:3000"]` | No |
| `WS_INITIAL_HOURS` | `int` | `1` | No |
| `GITHUB_TOKEN` | `str \| None` | `None` | No |
| `LOG_LEVEL` | `str` | `INFO` | No |

`CORS_ORIGINS` accepts a comma-separated string (e.g. `http://localhost:3000,http://localhost:3001`) which is split into a list by a `@field_validator`.

### `get_settings() -> Settings`

Returns a cached `Settings` instance (via `@lru_cache`). Call this instead of constructing `Settings()` directly so the configuration is parsed once and reused.

## Database (`app/database.py`)

### `get_engine() -> AsyncEngine`

Creates and caches an async SQLAlchemy engine using `create_async_engine` with `DATABASE_URL` from settings.

### `get_session_factory() -> async_sessionmaker[AsyncSession]`

Creates and caches an `async_sessionmaker` bound to the engine with `expire_on_commit=False`.

### `Base`

`DeclarativeBase` subclass. All ORM models must inherit from `Base`.

### `get_db() -> AsyncGenerator[AsyncSession]`

Async generator for use as a FastAPI dependency. Yields an `AsyncSession` and ensures it is closed after the request completes (even on exception) via `async with`.

Usage in a route:

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

@router.get("/items")
async def list_items(db: AsyncSession = Depends(get_db)):
    ...
```

## Application (`app/main.py`)

### FastAPI App

- **Title**: Team Statusboard
- **Version**: 0.1.0
- **Docs**: `/docs` (Swagger UI), `/redoc` (ReDoc)

### CORS Middleware

Configured from `settings.cors_origins`. Allows credentials, all methods, and all headers.

### Routes

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/health` | Returns `{"status": "ok"}` (unauthenticated) |

All API routes use the `/api/v1` prefix.

## Test Infrastructure

### Fixtures (`tests/conftest.py`)

| Fixture | Scope | Description |
|---|---|---|
| `test_settings` | function | `Settings` instance with `jwt_secret="test-secret-key"` and defaults |
| `client` | function | `httpx.AsyncClient` wired to the FastAPI app via `ASGITransport` |

### Running Tests

```bash
cd backend/
uv run pytest -v        # all tests, verbose
uv run ruff check app/ tests/  # lint
uv run mypy app/        # type check (strict)
```

### Quality Gates

- **Ruff**: target Python 3.13, line-length 88, rule sets E/F/I/N/UP/B/SIM/TCH
- **Mypy**: strict mode, pydantic plugin enabled
- **pytest-asyncio**: `asyncio_mode = "auto"` (no explicit markers needed)
