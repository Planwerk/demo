---
title: Backend Scaffold
quadrant: reference
---

# Backend Scaffold

Core modules that form the backend foundation: configuration, database layer, and application entry point.

## Project Structure

```
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

## Configuration (`app.config`)

The `Settings` class loads and validates all environment variables at import time using `pydantic-settings`. A module-level `settings` instance is exported for use throughout the application.

### Environment Variables

| Variable                    | Type           | Default                                                       | Required | Description                          |
| --------------------------- | -------------- | ------------------------------------------------------------- | -------- | ------------------------------------ |
| `DATABASE_URL`              | `str`          | `postgresql+asyncpg://user:pass@localhost:5432/statusboard`   | No       | PostgreSQL async connection string   |
| `JWT_SECRET`                | `str`          | --                                                            | Yes      | Secret key for JWT signing           |
| `JWT_ACCESS_EXPIRE_MINUTES` | `int`          | `30`                                                          | No       | Access token lifetime in minutes     |
| `JWT_REFRESH_EXPIRE_DAYS`   | `int`          | `7`                                                           | No       | Refresh token lifetime in days       |
| `CORS_ORIGINS`              | `str`          | `http://localhost:3000`                                       | No       | Comma-separated allowed CORS origins |
| `WS_INITIAL_HOURS`          | `int`          | `1`                                                           | No       | Hours of history sent on WS connect  |
| `GITHUB_TOKEN`              | `str \| None`  | `None`                                                        | No       | GitHub PAT for issue/PR enrichment   |
| `LOG_LEVEL`                 | `str`          | `INFO`                                                        | No       | Logging level                        |

### Exports

| Symbol              | Type       | Description                                                  |
| ------------------- | ---------- | ------------------------------------------------------------ |
| `Settings`          | class      | Pydantic `BaseSettings` subclass with all fields above       |
| `settings`          | `Settings` | Module-level singleton instance, validated at import time    |

### `Settings.cors_origins_list`

Property that splits `CORS_ORIGINS` by comma into a `list[str]`. Whitespace around each origin is stripped.

```python
# CORS_ORIGINS="http://localhost:3000,http://localhost:3001"
settings.cors_origins_list
# ['http://localhost:3000', 'http://localhost:3001']
```

### `.env` File Support

Settings are loaded from a `.env` file in the working directory (via `env_file=".env"`). Explicit environment variables take precedence over `.env` values.

## Database Layer (`app.database`)

Async SQLAlchemy 2.0 setup using the `asyncpg` driver.

### Exports

| Symbol              | Type                             | Description                                              |
| ------------------- | -------------------------------- | -------------------------------------------------------- |
| `async_engine`      | `AsyncEngine`                    | Engine created from `settings.DATABASE_URL` with `echo=False` |
| `AsyncSessionLocal` | `async_sessionmaker[AsyncSession]` | Session factory bound to `async_engine`, `expire_on_commit=False` |
| `Base`              | `DeclarativeBase` subclass       | Base class for all ORM models                            |
| `get_db`            | async generator                  | FastAPI dependency yielding `AsyncSession`               |

### `get_db()`

Async generator for use as a FastAPI dependency. Yields an `AsyncSession` scoped to the request lifecycle.

```python
async def get_db() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session
```

The `async with` context manager ensures the session is closed after the request completes, including on exceptions. Each request receives its own isolated session.

**Usage in endpoints:**

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

@router.get("/example")
async def example(db: AsyncSession = Depends(get_db)):
    ...
```

### `Base`

SQLAlchemy 2.0 `DeclarativeBase` subclass. All ORM models inherit from this class to register in `Base.metadata`.

```python
from app.database import Base

class User(Base):
    __tablename__ = "users"
    ...
```

## Application Entry Point (`app.main`)

### FastAPI App

Created as `FastAPI(title="Team Statusboard", version="0.1.0")`.

### CORS Middleware

`CORSMiddleware` is configured with:

| Parameter           | Value                        |
| ------------------- | ---------------------------- |
| `allow_origins`     | `settings.cors_origins_list` |
| `allow_credentials` | `True`                       |
| `allow_methods`     | `["*"]`                      |
| `allow_headers`     | `["*"]`                      |

### API Router

All API routes are mounted under a single `APIRouter` with `prefix="/api/v1"`.

### Endpoints

#### `GET /api/v1/health`

Health check endpoint. No authentication required. No database dependency.

**Response `200 OK`:**

```json
{"status": "ok"}
```

## CI Pipeline (`.github/workflows/ci.yml`)

Triggers on push to `main` and on pull requests.

### Jobs

| Job            | Runner          | Python | Description                                           |
| -------------- | --------------- | ------ | ----------------------------------------------------- |
| `lint`         | `ubuntu-latest` | 3.13   | Runs `uv run ruff check .` in `backend/`             |
| `test-backend` | `ubuntu-latest` | 3.13   | Runs `uv run pytest --tb=short -q` with PostgreSQL 17 |

The `test-backend` job starts a PostgreSQL 17 service container and sets `DATABASE_URL` and `JWT_SECRET` as environment variables.

## Tooling Configuration

### Ruff

Configured in `pyproject.toml` under `[tool.ruff]`:

- `target-version`: `py313`
- `line-length`: `99`
- Lint rules: `E`, `W`, `F`, `I`, `N`, `UP`, `B`, `A`, `S`, `T20`, `SIM`, `RUF`
- `S101` (assert) ignored globally; `S101`, `S106` ignored in `tests/`

### pytest

Configured in `pyproject.toml` under `[tool.pytest.ini_options]`:

- `asyncio_mode`: `auto` (async tests run without `@pytest.mark.asyncio`)
- `testpaths`: `["tests"]`
- `filterwarnings`: `["error"]` (warnings become errors)

### Coverage

Configured under `[tool.coverage]`:

- Source: `app`
- `fail_under`: `80`
