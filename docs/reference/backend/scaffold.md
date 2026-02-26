---
title: Backend Scaffold
quadrant: reference
---

# Backend Scaffold

Runtime configuration, database layer, and health endpoint provided by the backend foundation.

## Environment Variables

All variables are read by `app.config.Settings` (pydantic-settings) at startup. A `.env` file in `backend/` is loaded automatically; explicit environment variables take precedence.

| Variable | Type | Default | Required | Description |
|---|---|---|---|---|
| `DATABASE_URL` | `str` | `postgresql+asyncpg://user:pass@localhost:5432/statusboard` | No | Async SQLAlchemy connection string (must use `postgresql+asyncpg://` scheme) |
| `JWT_SECRET` | `str` | — | **Yes** | Signing key for HS256 JWT tokens. Missing value raises `ValidationError` at startup |
| `JWT_ACCESS_EXPIRE_MINUTES` | `int` | `30` | No | Access token lifetime in minutes |
| `JWT_REFRESH_EXPIRE_DAYS` | `int` | `7` | No | Refresh token lifetime in days |
| `CORS_ORIGINS` | `str` | `http://localhost:3000` | No | Comma-separated allowed origins for CORS |
| `WS_INITIAL_HOURS` | `int` | `1` | No | Hours of status history sent on WebSocket connect |
| `GITHUB_TOKEN` | `str \| None` | `None` | No | GitHub personal access token for metadata enrichment |
| `LOG_LEVEL` | `str` | `INFO` | No | Python log level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`) |

### Settings class

```python
from app.config import settings

# Access any field directly
settings.DATABASE_URL
settings.JWT_SECRET

# CORS origins as a list (splits on comma)
settings.cors_origins_list  # -> ["http://localhost:3000"]
```

## Database Module

`app.database` exports the async SQLAlchemy engine, session factory, ORM base class, and FastAPI dependency.

| Export | Type | Description |
|---|---|---|
| `async_engine` | `AsyncEngine` | Created via `create_async_engine(settings.DATABASE_URL, echo=False)` |
| `AsyncSessionLocal` | `async_sessionmaker[AsyncSession]` | Session factory bound to `async_engine` with `expire_on_commit=False` |
| `Base` | `DeclarativeBase` | SQLAlchemy 2.0 declarative base — all ORM models inherit from this |
| `get_db()` | `AsyncGenerator[AsyncSession]` | FastAPI dependency that yields a session and closes it on completion |

### get_db() usage

Inject as a FastAPI dependency to obtain a scoped database session per request:

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

@router.get("/items")
async def list_items(db: AsyncSession = Depends(get_db)):
    ...
```

The session is automatically closed when the request finishes (including on exceptions).

## Health Endpoint

| Method | Path | Auth | Response |
|---|---|---|---|
| `GET` | `/api/v1/health` | None | `200 {"status": "ok"}` |

No database query is executed — the endpoint stays responsive even if the database is unavailable.

## Project Structure

```
.github/
  workflows/
    ci.yml           # Lint + test jobs with PostgreSQL service container
backend/
  pyproject.toml
  app/
    __init__.py
    main.py          # FastAPI app, CORS middleware, API router
    config.py        # Settings (pydantic-settings)
    database.py      # Async engine, session factory, Base, get_db()
    models/          # ORM models (empty in scaffold)
    schemas/         # Pydantic request/response schemas (empty in scaffold)
    services/        # Business logic services (empty in scaffold)
    api/
      __init__.py
      routes/        # Route modules (empty in scaffold)
  tests/
    conftest.py
    unit/
    integration/
```

## CI Pipeline

`.github/workflows/ci.yml` triggers on push to `main` and on pull requests.

| Job | Python | Steps |
|---|---|---|
| `lint` | 3.13 | `uv sync --frozen` then `uv run ruff check .` |
| `test-backend` | 3.13 | PostgreSQL 17 service container, `uv sync --frozen` then `uv run pytest --tb=short -q` |
