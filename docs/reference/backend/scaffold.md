---
title: Backend Scaffold
quadrant: reference
---

# Backend Scaffold

## Project Structure

```
backend/
  pyproject.toml
  app/
    __init__.py
    main.py            # FastAPI application, CORS, API router
    config.py          # Settings (pydantic-settings)
    database.py        # Async engine, session factory, Base
    models/            # ORM models (empty scaffold)
    schemas/           # Pydantic schemas (empty scaffold)
    api/
      routes/          # API route modules (empty scaffold)
    services/          # Business logic (empty scaffold)
  tests/
    conftest.py
    unit/
    integration/
```

## Environment Variables

Defined in `app/config.py` via `Settings(BaseSettings)`. Supports `.env` file loading.

| Variable | Type | Default | Required | Description |
|---|---|---|---|---|
| `DATABASE_URL` | `str` | `postgresql+asyncpg://user:pass@localhost:5432/statusboard` | No | Async SQLAlchemy connection URL (must use `asyncpg` driver) |
| `JWT_SECRET` | `str` | — | **Yes** | Secret key for signing JWT tokens. Missing value raises `ValidationError` at startup |
| `JWT_ACCESS_EXPIRE_MINUTES` | `int` | `30` | No | Access token lifetime in minutes |
| `JWT_REFRESH_EXPIRE_DAYS` | `int` | `7` | No | Refresh token lifetime in days |
| `CORS_ORIGINS` | `str` | `http://localhost:3000` | No | Comma-separated list of allowed CORS origins |
| `WS_INITIAL_HOURS` | `int` | `1` | No | Initial WebSocket connection window in hours |
| `GITHUB_TOKEN` | `str \| None` | `None` | No | GitHub personal access token for integration features |
| `LOG_LEVEL` | `str` | `INFO` | No | Python logging level |

### Settings Instance

A module-level `settings` instance is exported from `app.config`:

```python
from app.config import settings
```

### CORS Origins List

`settings.cors_origins_list` splits `CORS_ORIGINS` by comma and strips whitespace, returning `list[str]`.

## Database Module

Defined in `app/database.py`. All exports use async SQLAlchemy 2.0 APIs.

### Exports

| Symbol | Type | Description |
|---|---|---|
| `async_engine` | `AsyncEngine` | Created via `create_async_engine(settings.DATABASE_URL, echo=False)` |
| `AsyncSessionLocal` | `async_sessionmaker[AsyncSession]` | Session factory bound to `async_engine` with `expire_on_commit=False` |
| `Base` | `DeclarativeBase` | Base class for all ORM models |
| `get_db()` | `AsyncGenerator[AsyncSession, None]` | FastAPI dependency yielding a session per request |

### get_db() Lifecycle

- Opens a session via `AsyncSessionLocal()` as an async context manager
- Yields the session to the caller
- On exception: rolls back the session, then re-raises
- Session is always closed when the context manager exits

Usage in endpoints:

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

@router.get("/items")
async def list_items(db: AsyncSession = Depends(get_db)):
    ...
```

## API Endpoints

Base path: `/api/v1` (via `APIRouter(prefix="/api/v1")` in `app/main.py`).

### GET /api/v1/health

Health check endpoint. No authentication required. No database dependency.

**Response** `200 OK`

```json
{"status": "ok"}
```

## CORS Middleware

Added to the FastAPI app in `app/main.py`:

| Parameter | Value |
|---|---|
| `allow_origins` | `settings.cors_origins_list` |
| `allow_credentials` | `True` |
| `allow_methods` | `["*"]` |
| `allow_headers` | `["*"]` |

## CI Pipeline

Defined in `.github/workflows/ci.yml`. Triggers on push to `main` and on pull requests.

### Jobs

| Job | Python | Steps |
|---|---|---|
| `lint` | 3.13 | `uv sync --frozen` then `uv run ruff check .` |
| `test-backend` | 3.13 | PostgreSQL 17 service container, `uv sync --frozen` then `uv run pytest --tb=short -q` |

The `test-backend` job sets `DATABASE_URL` and `JWT_SECRET` environment variables pointing to the service container.

## Toolchain

| Tool | Config Location | Command |
|---|---|---|
| ruff | `pyproject.toml` `[tool.ruff]` | `uv run ruff check .` |
| pytest | `pyproject.toml` `[tool.pytest.ini_options]` | `uv run pytest` |
| mypy | `pyproject.toml` `[tool.mypy]` | `uv run mypy app` |

Ruff rules: `E`, `F`, `I`, `UP`, `B`, `SIM` with `target-version = "py313"` and `line-length = 99`.

Pytest: `asyncio_mode = "auto"`, `testpaths = ["tests"]`.
