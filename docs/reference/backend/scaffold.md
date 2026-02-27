---
title: Backend Scaffold
quadrant: reference
---

# Backend Scaffold

The backend scaffold provides the project foundation: configuration loading, async database connectivity, CORS-enabled FastAPI application, and a health check endpoint. All subsequent features build on these modules.

## Project Structure

```
.github/
└── workflows/
    └── ci.yml           # Lint + test CI pipeline
backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app, CORS middleware, API router
│   ├── config.py        # Settings via pydantic-settings
│   ├── database.py      # Async SQLAlchemy engine, session factory, Base
│   ├── models/          # ORM models (empty in scaffold)
│   ├── schemas/         # Pydantic request/response schemas (empty in scaffold)
│   ├── api/
│   │   ├── routes/      # API route handlers (empty in scaffold)
│   │   └── __init__.py
│   └── services/        # Business logic (empty in scaffold)
├── tests/
│   ├── conftest.py
│   ├── unit/
│   └── integration/
└── pyproject.toml
```

## Environment Variables

All variables are loaded by `app.config.Settings` using `pydantic-settings`. Values can be set via environment variables or a `.env` file in the backend directory. Explicit environment variables take precedence over `.env` values.

| Variable | Type | Default | Required | Description |
|---|---|---|---|---|
| `DATABASE_URL` | `str` | `postgresql+asyncpg://user:pass@localhost:5432/statusboard` | No | PostgreSQL connection string (must use `asyncpg` driver) |
| `JWT_SECRET` | `str` | — | **Yes** | Secret key for JWT signing. Missing value raises `ValidationError` at startup |
| `JWT_ACCESS_EXPIRE_MINUTES` | `int` | `30` | No | Access token expiry in minutes |
| `JWT_REFRESH_EXPIRE_DAYS` | `int` | `7` | No | Refresh token expiry in days |
| `CORS_ORIGINS` | `str` | `http://localhost:3000` | No | Comma-separated list of allowed CORS origins |
| `WS_INITIAL_HOURS` | `int` | `1` | No | Hours of status history sent on WebSocket connect |
| `GITHUB_TOKEN` | `str \| None` | `None` | No | GitHub personal access token for enriching issue/PR metadata |
| `LOG_LEVEL` | `str` | `INFO` | No | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |

### `cors_origins_list` Property

`Settings.cors_origins_list` splits the `CORS_ORIGINS` string by comma and strips whitespace, returning a `list[str]`. This list is passed directly to `CORSMiddleware.allow_origins`.

```python
from app.config import settings

settings.cors_origins_list
# With CORS_ORIGINS="http://localhost:3000,http://localhost:3001"
# Returns: ["http://localhost:3000", "http://localhost:3001"]
```

## Database Module

**Module:** `app.database`

### Exports

| Symbol | Type | Description |
|---|---|---|
| `async_engine` | `AsyncEngine` | Async SQLAlchemy engine created with `create_async_engine` using `DATABASE_URL`. Echo is disabled. |
| `AsyncSessionLocal` | `async_sessionmaker[AsyncSession]` | Session factory bound to `async_engine` with `expire_on_commit=False`. |
| `Base` | `DeclarativeBase` | SQLAlchemy 2.0 declarative base class. All ORM models inherit from this. |
| `get_db()` | `AsyncGenerator[AsyncSession]` | FastAPI dependency that yields an `AsyncSession`. |

### `get_db()`

Async generator for FastAPI dependency injection. Uses `async with` on `AsyncSessionLocal()` to ensure the session is closed after the request completes, including on exceptions.

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

@router.get("/example")
async def example(db: AsyncSession = Depends(get_db)):
    ...
```

Each request receives its own isolated session. The `async with` context manager guarantees cleanup regardless of success or failure.

## Health Check Endpoint

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/api/v1/health` | None | Returns application health status |

### Response

**Status:** `200 OK`

```json
{
  "status": "ok"
}
```

The health check has no database dependency and responds even if the database is unavailable.

## FastAPI Application

**Module:** `app.main`

The `app` instance is a `FastAPI` application with:

- **Title:** Team Statusboard
- **Version:** 0.1.0
- **CORS Middleware:** Origins from `settings.cors_origins_list`, credentials allowed, all methods and headers permitted.
- **API Router:** Prefix `/api/v1` — all API endpoints are mounted under this prefix.

## CI Pipeline

**File:** `.github/workflows/ci.yml`

Triggers on push to `main` and on pull requests.

| Job | Runner | Description |
|---|---|---|
| `lint` | `ubuntu-latest` | Installs uv, runs `uv run ruff check .` and `uv run mypy app/ --strict` in `backend/` |
| `test-backend` | `ubuntu-latest` | Starts PostgreSQL 17 service container, runs `uv run pytest --tb=short -q` in `backend/` |

Both jobs use Python 3.13. The `test-backend` job sets `DATABASE_URL` and `JWT_SECRET` as environment variables pointing to the PostgreSQL service container.

## Tooling Configuration

Configured in `backend/pyproject.toml`:

- **Ruff:** `target-version = "py313"`, `line-length = 99`, rules: `E`, `F`, `I`, `UP`, `B`, `SIM`. First-party import: `app`.
- **Mypy:** `strict = true`, pydantic plugin enabled. Ignores missing imports for `asyncpg`.
- **Pytest:** `asyncio_mode = "auto"`, `testpaths = ["tests"]`.
