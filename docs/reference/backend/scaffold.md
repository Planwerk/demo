---
title: Backend Scaffold
quadrant: backend
---

# Backend Scaffold

Project foundation: configuration, database layer, and FastAPI application entry point.

## Module Overview

| Module   | Path              | Purpose                                       |
| -------- | ----------------- | --------------------------------------------- |
| config   | `app/config.py`   | Environment-based settings via pydantic-settings |
| database | `app/database.py` | Async SQLAlchemy engine, session factory, ORM base |
| main     | `app/main.py`     | FastAPI app, CORS middleware, API router       |

## `app/config.py` — Configuration

### `Settings`

Extends `pydantic_settings.BaseSettings`. Loads values from environment variables and `.env` files.

| Field                        | Type           | Default                                                    | Required | Description                              |
| ---------------------------- | -------------- | ---------------------------------------------------------- | -------- | ---------------------------------------- |
| `database_url`               | `str`          | `postgresql+asyncpg://user:pass@localhost:5432/statusboard` | No       | Async SQLAlchemy connection string       |
| `jwt_secret`                 | `str`          | —                                                          | **Yes**  | Secret key for JWT signing               |
| `jwt_access_expire_minutes`  | `int`          | `30`                                                       | No       | Access token lifetime in minutes         |
| `jwt_refresh_expire_days`    | `int`          | `7`                                                        | No       | Refresh token lifetime in days           |
| `cors_origins`               | `list[str]`    | `["http://localhost:3000"]`                                | No       | Allowed CORS origins                     |
| `ws_initial_hours`           | `int`          | `1`                                                        | No       | Hours of history sent on WebSocket connect |
| `github_token`               | `str \| None`  | `None`                                                     | No       | GitHub PAT for issue/PR metadata enrichment |
| `log_level`                  | `str`          | `"INFO"`                                                   | No       | Logging level                            |

**CORS_ORIGINS parsing:** When set as an environment variable, `CORS_ORIGINS` accepts either a JSON array or a comma-separated string (e.g. `http://localhost:3000,http://localhost:3001`). A custom `_CorsAwareEnvSource` attempts JSON parsing first, falling back to comma splitting via a `@field_validator`.

### `get_settings() -> Settings`

Returns a cached `Settings` instance (via `@lru_cache`). The singleton is created on first call. Call `get_settings.cache_clear()` in tests to reset.

## `app/database.py` — Database Layer

### `Base`

`sqlalchemy.orm.DeclarativeBase` subclass. All ORM models must inherit from this class.

### `get_engine() -> AsyncEngine`

Returns a cached async SQLAlchemy engine created from `settings.database_url`. Uses `@lru_cache` so only one engine exists per process.

### `get_session_factory() -> async_sessionmaker[AsyncSession]`

Returns an `async_sessionmaker` bound to the engine with `expire_on_commit=False`.

### `get_db() -> AsyncGenerator[AsyncSession]`

FastAPI dependency. Yields an `AsyncSession` via `async with session_factory() as session`, ensuring the session is closed after the request completes (including on exceptions).

**Usage in route handlers:**

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

@router.get("/items")
async def list_items(db: AsyncSession = Depends(get_db)):
    ...
```

## `app/main.py` — Application Entry Point

### `app`

`FastAPI` instance with `title="Team Statusboard"` and `version="0.1.0"`.

**CORS middleware** is configured from `settings.cors_origins` with:
- `allow_credentials=True`
- `allow_methods=["*"]`
- `allow_headers=["*"]`

### `api_router`

`APIRouter` with `prefix="/api/v1"`. All versioned endpoints are mounted on this router.

### Endpoints

| Method | Path             | Auth | Response           |
| ------ | ---------------- | ---- | ------------------ |
| GET    | `/api/v1/health` | None | `{"status": "ok"}` |
| GET    | `/docs`          | None | Swagger UI (HTML)  |
| GET    | `/redoc`         | None | ReDoc (HTML)       |

### Running the server

```bash
cd backend
uv run fastapi dev app/main.py --port 8000
```

## Directory Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── config.py          # Settings class, get_settings()
│   ├── database.py        # Engine, session factory, Base, get_db()
│   ├── main.py            # FastAPI app, CORS, health check
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/
│   │       └── __init__.py
│   ├── models/
│   │   └── __init__.py
│   ├── schemas/
│   │   └── __init__.py
│   └── services/
│       └── __init__.py
├── tests/
│   ├── conftest.py        # Shared fixtures
│   └── unit/
│       ├── test_config.py
│       ├── test_database.py
│       └── test_main.py
└── pyproject.toml
```

## Test Infrastructure

**pytest** is configured with `asyncio_mode = "auto"` in `pyproject.toml`, so async test functions run without explicit markers.

### Shared Fixtures (`tests/conftest.py`)

| Fixture          | Scope              | Description                                                                      |
| ---------------- | ------------------ | -------------------------------------------------------------------------------- |
| `_clear_caches`  | function (autouse) | Clears `get_settings` and `get_engine` `lru_cache` between tests                 |
| `test_settings`  | function           | `Settings` instance with `jwt_secret="test-secret-key"` and SQLite in-memory DB  |
| `async_client`   | function           | `httpx.AsyncClient` wired to the FastAPI app via `ASGITransport`                 |

### Quality Gates

```bash
cd backend

# Lint (ruff — Python 3.13, line-length 88)
.venv/bin/python -m ruff check app/ tests/

# Type check (mypy — strict mode, pydantic plugin)
.venv/bin/python -m mypy app/

# Tests
.venv/bin/python -m pytest -v
```

## Dependencies

### Production

fastapi, uvicorn[standard], sqlalchemy, asyncpg, pydantic-settings, structlog, bcrypt, pyjwt, httpx, alembic

### Development

pytest, pytest-asyncio, httpx, ruff, mypy, aiosqlite
