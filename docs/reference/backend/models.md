---
title: ORM Models Reference
quadrant: reference
---

# ORM Models Reference

## Import

All models are exported from the `app.models` package:

```python
from app.models import User, StatusUpdate
```

Both models inherit from `Base` (defined in `app.database`) and are registered with `Base.metadata` on import.

## User

Module: `app.models.user`

Table: `users`

| Column | Type | Constraints | Default |
|---|---|---|---|
| `id` | `Uuid` | Primary key | `uuid4()` |
| `username` | `String(50)` | Unique, not null | — |
| `display_name` | `String(100)` | Not null | — |
| `email` | `String(255)` | Unique, not null | — |
| `password_hash` | `String(255)` | Not null | — |
| `avatar_url` | `String(500)` | Nullable | `None` |
| `xp` | `Integer` | Not null | `0` |
| `current_streak` | `Integer` | Not null | `0` |
| `longest_streak` | `Integer` | Not null | `0` |
| `last_post_date` | `Date` | Nullable | `None` |
| `created_at` | `DateTime` (timezone-aware) | Not null | `datetime.now(UTC)` |

### Relationships

| Attribute | Target | Loading | Cascade |
|---|---|---|---|
| `status_updates` | `list[StatusUpdate]` | `selectin` | `all, delete-orphan` |

Bidirectional via `back_populates="user"`.

## StatusUpdate

Module: `app.models.status`

Table: `status_updates`

| Column | Type | Constraints | Default |
|---|---|---|---|
| `id` | `Uuid` | Primary key | `uuid4()` |
| `user_id` | `Uuid` | FK → `users.id`, not null, indexed | — |
| `message` | `Text` | Not null | — |
| `category` | `String(20)` | Not null | — |
| `created_at` | `DateTime` (timezone-aware) | Not null | `datetime.now(UTC)` |

### Relationships

| Attribute | Target | Loading |
|---|---|---|
| `user` | `User` | `joined` |

Bidirectional via `back_populates="status_updates"`.

## Alembic Configuration

Alembic is configured for async SQLAlchemy in `backend/alembic.ini` and `backend/alembic/env.py`.

### Setup

- `alembic.ini` sets `script_location = alembic` and a placeholder `sqlalchemy.url` (overridden by `env.py`)
- `env.py` imports `settings.DATABASE_URL` from `app.config` and uses `create_async_engine` with `NullPool`
- `env.py` imports `User` and `StatusUpdate` to register them with `Base.metadata` for autogenerate support
- `target_metadata = Base.metadata` enables schema diffing

### Commands

Run from the `backend/` directory:

```bash
# Apply all migrations
alembic upgrade head

# Revert all migrations
alembic downgrade base

# Generate a new migration after model changes
alembic revision --autogenerate -m "description"
```

### Migration: Initial tables

File: `alembic/versions/2026_02_28_2200-a1b2c3d4e5f6_initial_users_and_status_updates.py`

- **Upgrade:** Creates `users` table, then `status_updates` table (with FK to `users.id`)
- **Downgrade:** Drops `status_updates` first (FK dependency), then `users`
