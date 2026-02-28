---
title: Backend Scaffold
quadrant: reference
---

# Backend Scaffold

Module reference for the backend foundation: configuration, database layer, and health endpoint.

## Project Structure

```
backend/
├── pyproject.toml          # Dependencies, tool config (ruff, pytest, mypy)
├── app/
│   ├── __init__.py
│   ├── config.py           # Settings class (pydantic-settings)
│   ├── database.py         # Async engine, session factory, Base, get_db()
│   ├── main.py             # FastAPI app, CORS middleware, API router
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
└── tests/
    └── unit/
        ├── test_config.py
        ├── test_database.py
        ├── test_main.py
        └── test_scaffold.py
```

## Environment Variables

All variables are defined in `app.config.Settings` and read from the process environment or a `.env` file.

| Variable | Type | Default | Required | Description |
|---|---|---|---|---|
| `DATABASE_URL` | `str` | `postgresql+asyncpg://localhost:5432/statusboard` | No | Async SQLAlchemy connection string |
| `JWT_SECRET` | `str` | — | **Yes** | Signing key for JWT tokens |
| `JWT_ACCESS_EXPIRE_MINUTES` | `int` | `30` | No | Access token lifetime in minutes |
| `JWT_REFRESH_EXPIRE_DAYS` | `int` | `7` | No | Refresh token lifetime in days |
| `CORS_ORIGINS` | `str` | `http://localhost:3000` | No | Comma-separated allowed origins |
| `WS_INITIAL_HOURS` | `int` | `1` | No | Hours of history sent on WebSocket connect |
| `GITHUB_TOKEN` | `str \| None` | `None` | No | GitHub API token for link enrichment |
| `LOG_LEVEL` | `str` | `INFO` | No | Python logging level |

Settings are validated at import time. A missing `JWT_SECRET` raises `pydantic.ValidationError`.

## `app.config`

**Module:** `app/config.py`

### `Settings`

```python
from app.config import Settings, settings
```

`BaseSettings` subclass with `SettingsConfigDict(env_file=".env")`. Field names are lowercase; environment variables are matched case-insensitively by pydantic-settings (e.g., `JWT_SECRET` maps to `jwt_secret`).

### `settings`

Module-level `Settings()` instance. Import this wherever configuration values are needed.

## `app.database`

**Module:** `app/database.py`

### `async_engine`

```python
from app.database import async_engine
```

`AsyncEngine` created with `create_async_engine(settings.database_url, echo=False)`. Uses the `asyncpg` dialect.

### `AsyncSessionLocal`

```python
from app.database import AsyncSessionLocal
```

`async_sessionmaker` bound to `async_engine` with `expire_on_commit=False`.

### `Base`

```python
from app.database import Base
```

`DeclarativeBase` subclass (SQLAlchemy 2.0 style). All ORM models inherit from this class.

### `get_db()`

```python
from app.database import get_db
```

Async generator yielding an `AsyncSession`. Use as a FastAPI dependency:

```python
@router.get("/example")
async def example(db: AsyncSession = Depends(get_db)):
    ...
```

Session lifecycle:
- Opens via `AsyncSessionLocal()` context manager
- Rolls back on unhandled exception
- Closes automatically on exit (success or failure)

## `app.main`

**Module:** `app/main.py`

### `app`

```python
from app.main import app
```

`FastAPI` instance with `title="Team Statusboard"`. CORS middleware is configured from `settings.cors_origins` (split on `,`), with `allow_credentials=True`, `allow_methods=["*"]`, `allow_headers=["*"]`.

### `api_router`

```python
from app.main import api_router
```

`APIRouter` with `prefix="/api/v1"`. All versioned endpoints are registered on this router.

## Health Endpoint

```
GET /api/v1/health
```

Returns service health status. No authentication required.

**Response** `200 OK`

```json
{"status": "ok"}
```

This endpoint has no database dependency and remains responsive even if the database is unavailable.

## Toolchain

| Command | Purpose |
|---|---|
| `uv sync --dev` | Install all dependencies |
| `uv run fastapi dev app/main.py --port 8000` | Start dev server |
| `uv run pytest --tb=short -q` | Run tests |
| `uv run ruff check .` | Lint |
| `uv run mypy app/` | Type check |
