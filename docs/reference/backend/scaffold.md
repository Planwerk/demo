---
title: Backend Scaffold
quadrant: reference
---

# Backend Scaffold

Core modules that form the foundation of the FastAPI backend: configuration, database layer, and application entry point.

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app, CORS, health check
│   ├── config.py         # pydantic-settings configuration
│   ├── database.py       # Async SQLAlchemy engine & session
│   ├── models/           # ORM models (empty in scaffold)
│   ├── schemas/          # Pydantic request/response schemas
│   ├── api/
│   │   └── routes/       # API route handlers
│   └── services/         # Business logic layer
├── tests/
│   ├── conftest.py
│   ├── unit/
│   └── integration/
└── pyproject.toml
```

## Environment Variables

All configuration is managed by the `Settings` class in `app/config.py` using `pydantic-settings`. Values are read from environment variables, with `.env` file support.

| Variable | Type | Default | Required | Description |
|---|---|---|---|---|
| `DATABASE_URL` | `str` | `postgresql+asyncpg://user:pass@localhost:5432/statusboard` | No | Async SQLAlchemy connection string (must use `asyncpg` driver) |
| `JWT_SECRET` | `str` | — | **Yes** | Secret key for signing JWT tokens |
| `JWT_ACCESS_EXPIRE_MINUTES` | `int` | `30` | No | Access token lifetime in minutes |
| `JWT_REFRESH_EXPIRE_DAYS` | `int` | `7` | No | Refresh token lifetime in days |
| `CORS_ORIGINS` | `str` | `http://localhost:3000` | No | Comma-separated allowed origins |
| `WS_INITIAL_HOURS` | `int` | `1` | No | Hours of history sent on WebSocket connect |
| `GITHUB_TOKEN` | `str \| None` | `None` | No | GitHub API token for reference enrichment |
| `LOG_LEVEL` | `str` | `INFO` | No | Logging level |

Missing `JWT_SECRET` raises a `pydantic.ValidationError` at import time.

### Usage

```python
from app.config import settings

settings.DATABASE_URL       # str
settings.cors_origins_list  # list[str] — splits CORS_ORIGINS by comma
```

## Database Module

`app/database.py` exports the async SQLAlchemy primitives used throughout the application.

### Exports

| Symbol | Type | Description |
|---|---|---|
| `async_engine` | `AsyncEngine` | Created via `create_async_engine(settings.DATABASE_URL, echo=False)` |
| `AsyncSessionLocal` | `async_sessionmaker[AsyncSession]` | Session factory bound to `async_engine`, `expire_on_commit=False` |
| `Base` | `DeclarativeBase` | SQLAlchemy 2.0 declarative base for ORM model inheritance |
| `get_db()` | `AsyncGenerator[AsyncSession, None]` | FastAPI dependency that yields a session and closes it on completion |

### `get_db()` Dependency

Yields an `AsyncSession` using `async with AsyncSessionLocal()`, ensuring the session is closed after the request completes (including on exceptions).

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

@router.get("/items")
async def list_items(db: AsyncSession = Depends(get_db)):
    ...
```

## API Endpoints

Base path: `/api/v1`

### `GET /api/v1/health`

Health check endpoint. No authentication required. Does not query the database.

**Response** `200 OK`

```json
{"status": "ok"}
```

## CORS Configuration

`CORSMiddleware` is added to the FastAPI app with:

| Parameter | Value |
|---|---|
| `allow_origins` | `settings.cors_origins_list` |
| `allow_credentials` | `True` |
| `allow_methods` | `["*"]` |
| `allow_headers` | `["*"]` |

## CI Pipeline

`.github/workflows/ci.yml` runs on push to `main` and on pull requests.

| Job | Python | Steps |
|---|---|---|
| `lint` | 3.13 | `uv sync --frozen` then `uv run ruff check .` |
| `test-backend` | 3.13 | PostgreSQL 17 service container, `uv sync --frozen` then `uv run pytest --tb=short -q` |
