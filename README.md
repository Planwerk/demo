# Team Statusboard

A real-time team status update application — like an async standup board — built with **FastAPI** (backend) and **Next.js** (frontend). This project serves as a demonstration for **LLM-driven development**, showcasing how to build a full-stack application with comprehensive testing using AI-assisted workflows.

## Overview

Team members register, log in, and post short status updates (similar to daily standups) that are displayed chronologically. Updates appear in real time via WebSockets, are persisted in a database, and can be viewed by the entire team. Status updates can reference GitHub Issues and Pull Requests, which are rendered as rich links. A gamification system with streaks, XP, and achievements keeps the team engaged.

### Key Features

- **User accounts** — registration, login (JWT-based), profile with avatar
- **Post status updates** with message, category, and automatic timestamp
- **Real-time feed** — new updates appear instantly for all connected clients via WebSocket
- **Chronological list** — updates displayed newest-first with infinite scroll
- **Database persistence** — all data stored in PostgreSQL
- **Category tags** — updates can be tagged (`done`, `in-progress`, `blocked`, `planning`)
- **GitHub linking** — reference Issues and PRs (e.g. `org/repo#42`) with auto-detected rich previews
- **Filter & search** — filter updates by user, category, or date range
- **Gamification** — XP, streaks, achievements, and a team leaderboard

## Architecture

```
┌─────────────────────┐       ┌─────────────────────┐       ┌──────────────┐
│                     │  HTTP │                     │       │              │
│   Next.js Frontend  │◄─────►│   FastAPI Backend   │◄─────►│  PostgreSQL  │
│   (Port 3000)       │  WS   │   (Port 8000)       │       │  (Port 5432) │
│                     │◄─────►│                     │       │              │
└─────────────────────┘       └─────────────────────┘       └──────────────┘
                                       │
                                       │ GitHub API (optional)
                                       ▼
                              ┌─────────────────┐
                              │  api.github.com │
                              └─────────────────┘
```

### Backend (FastAPI)

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                # FastAPI application entry point
│   ├── config.py              # Settings via pydantic-settings
│   ├── database.py            # SQLAlchemy async engine & session
│   ├── logging.py             # structlog configuration (JSON output, request-ID middleware)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py            # SQLAlchemy ORM model: User
│   │   ├── status.py          # SQLAlchemy ORM model: StatusUpdate
│   │   ├── github_link.py     # SQLAlchemy ORM model: GitHubLink
│   │   └── achievement.py     # SQLAlchemy ORM models: Achievement, UserAchievement
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py            # Pydantic schemas for user & auth
│   │   ├── status.py          # Pydantic request/response schemas
│   │   ├── github_link.py     # Pydantic schemas for GitHub references
│   │   └── gamification.py    # Pydantic schemas for XP, streaks, achievements
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py            # Dependency injection (current user, DB session)
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py        # Register, login, token refresh
│   │   │   ├── users.py       # User profile endpoints
│   │   │   ├── status.py      # Status update CRUD
│   │   │   └── gamification.py # Leaderboard, achievements, streaks
│   │   └── websocket.py       # WebSocket endpoint for real-time updates
│   └── services/
│       ├── __init__.py
│       ├── auth.py            # Password hashing, JWT creation/validation
│       ├── user.py            # User CRUD operations
│       ├── status.py          # Status update business logic
│       ├── github_link.py     # GitHub reference parsing & metadata fetching
│       └── gamification.py    # XP calculation, streak tracking, achievement checks
├── alembic/
│   ├── env.py
│   └── versions/              # Database migrations
├── tests/
│   ├── conftest.py            # Shared fixtures (async DB, test client, auth helpers)
│   ├── unit/
│   │   ├── test_schemas.py    # Pydantic schema validation
│   │   ├── test_services.py   # Service layer with mocked DB
│   │   ├── test_github_parser.py # GitHub reference parsing
│   │   └── test_gamification.py  # XP & achievement logic
│   └── integration/
│       ├── test_auth.py       # Registration & login flow
│       ├── test_api.py        # Status endpoint tests against test DB
│       └── test_websocket.py  # WebSocket connection tests
├── alembic.ini
├── pyproject.toml
└── Dockerfile
```

### Frontend (Next.js)

```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx           # Root layout with providers
│   │   ├── page.tsx             # Main statusboard page
│   │   ├── login/
│   │   │   └── page.tsx         # Login page
│   │   ├── register/
│   │   │   └── page.tsx         # Registration page
│   │   ├── profile/
│   │   │   └── [username]/
│   │   │       └── page.tsx     # User profile with stats & achievements
│   │   ├── leaderboard/
│   │   │   └── page.tsx         # Team leaderboard
│   │   └── globals.css          # Global styles (Tailwind)
│   ├── components/
│   │   ├── StatusFeed.tsx       # Chronological update list
│   │   ├── StatusCard.tsx       # Single status update card
│   │   ├── StatusForm.tsx       # Form to post a new update
│   │   ├── FilterBar.tsx        # Filter by user/category/date
│   │   ├── ConnectionBadge.tsx  # WebSocket connection indicator
│   │   ├── GitHubRefBadge.tsx   # Rendered GitHub issue/PR link
│   │   ├── UserAvatar.tsx       # User avatar with online indicator
│   │   ├── StreakBanner.tsx     # Current streak display
│   │   ├── AchievementToast.tsx # Achievement unlock notification
│   │   └── LeaderboardTable.tsx # XP leaderboard table
│   ├── hooks/
│   │   ├── useWebSocket.ts     # WebSocket connection management
│   │   ├── useStatusUpdates.ts # Data fetching & state
│   │   └── useAuth.ts          # Authentication state & token management
│   ├── lib/
│   │   ├── api.ts              # API client (fetch wrapper with auth)
│   │   ├── types.ts            # TypeScript interfaces
│   │   └── github.ts           # GitHub reference regex & helpers
│   └── __tests__/
│       ├── unit/
│       │   ├── StatusCard.test.tsx
│       │   ├── StatusForm.test.tsx
│       │   ├── GitHubRefBadge.test.tsx
│       │   ├── FilterBar.test.tsx
│       │   └── gamification.test.tsx
│       └── integration/
│           ├── StatusFeed.test.tsx
│           └── auth-flow.test.tsx
├── e2e/
│   ├── statusboard.spec.ts     # Full E2E: post, view, real-time
│   ├── auth.spec.ts            # Registration & login E2E
│   ├── github-links.spec.ts    # GitHub reference rendering E2E
│   ├── gamification.spec.ts    # Achievements & leaderboard E2E
│   └── fixtures/               # Playwright test fixtures
├── next.config.ts
├── tailwind.config.ts
├── tsconfig.json
├── package.json
├── Dockerfile
└── playwright.config.ts
```

### Infrastructure

```
├── docker-compose.yml          # All services (backend, frontend, db)
├── docker-compose.test.yml     # Test environment with test DB
├── .env.example                # Environment variable template
├── Makefile                    # Common commands (dev, test, lint, migrate)
└── .github/
    └── workflows/
        └── ci.yml              # CI pipeline (lint, test, e2e)
```

#### Makefile Targets

| Target                | Description                                           |
| --------------------- | ----------------------------------------------------- |
| `make dev`            | Start all services in development mode                |
| `make dev-backend`    | Start only the backend dev server                     |
| `make dev-frontend`   | Start only the frontend dev server                    |
| `make test`           | Run all tests (backend + frontend)                    |
| `make test-backend`   | Run backend unit + integration tests                  |
| `make test-frontend`  | Run frontend unit + integration tests                 |
| `make test-e2e`       | Run Playwright end-to-end tests                       |
| `make lint`           | Run all linters (ruff + eslint)                       |
| `make lint-fix`       | Auto-fix lint issues                                  |
| `make migrate`        | Run Alembic migrations (`alembic upgrade head`)       |
| `make migrate-create` | Create a new Alembic migration                        |
| `make seed`           | Seed the database (achievements + optional demo user) |
| `make build`          | Build Docker images for all services                  |
| `make clean`          | Remove containers, volumes, and build artifacts       |

## Tech Stack

| Layer     | Technology                                                        |
| --------- | ----------------------------------------------------------------- |
| Frontend  | Next.js 15 (App Router), React 19, TypeScript, Tailwind CSS       |
| Backend   | FastAPI, Python 3.13, SQLAlchemy 2 (async), Pydantic v2           |
| Auth      | JWT (access + refresh tokens), bcrypt password hashing            |
| Database  | PostgreSQL 17, Alembic (migrations)                               |
| WebSocket | FastAPI WebSocket, native browser WebSocket API                   |
| Testing   | pytest + pytest-asyncio, Jest + React Testing Library, Playwright |
| DevOps    | Docker, Docker Compose                                            |
| Linting   | Ruff (Python), ESLint + Prettier (TypeScript)                     |
| Logging   | structlog (structured JSON), request-ID middleware                |

**Frontend state management:**
- Auth state — React Context (`AuthProvider`)
- Server data — direct `fetch` + WebSocket, no external state library
- UI state — local component state via `useState`

## Data Model

### User

| Field            | Type         | Description                                |
| ---------------- | ------------ | ------------------------------------------ |
| `id`             | UUID         | Primary key                                |
| `username`       | VARCHAR(50)  | Unique username                            |
| `display_name`   | VARCHAR(100) | Display name shown in the UI               |
| `email`          | VARCHAR(255) | Unique email address                       |
| `password_hash`  | VARCHAR(255) | bcrypt-hashed password                     |
| `avatar_url`     | VARCHAR(500) | URL to avatar image (nullable)             |
| `xp`             | INTEGER      | Total experience points (default: 0)       |
| `current_streak` | INTEGER      | Consecutive days with updates (default: 0) |
| `longest_streak` | INTEGER      | All-time longest streak (default: 0)       |
| `last_post_date` | DATE         | Date of the most recent post (nullable)    |
| `created_at`     | TIMESTAMP    | Account creation time (UTC)                |

### StatusUpdate

| Field        | Type        | Description                                          |
| ------------ | ----------- | ---------------------------------------------------- |
| `id`         | UUID        | Primary key                                          |
| `user_id`    | UUID (FK)   | References `User.id`                                 |
| `message`    | TEXT        | The status update content (max 500 chars)            |
| `category`   | VARCHAR(20) | One of: `done`, `in-progress`, `blocked`, `planning` |
| `created_at` | TIMESTAMP   | Auto-set on creation (UTC)                           |

### GitHubLink

| Field       | Type         | Description                                                              |
| ----------- | ------------ | ------------------------------------------------------------------------ |
| `id`        | UUID         | Primary key                                                              |
| `status_id` | UUID (FK)    | References `StatusUpdate.id`                                             |
| `owner`     | VARCHAR(100) | GitHub repository owner (e.g. `facebook`)                                |
| `repo`      | VARCHAR(100) | GitHub repository name (e.g. `react`)                                    |
| `number`    | INTEGER      | Issue or PR number                                                       |
| `type`      | VARCHAR(10)  | `issue` or `pull_request` (resolved via GitHub API or left as `unknown`) |
| `title`     | VARCHAR(500) | Fetched title from GitHub (nullable, cached)                             |
| `state`     | VARCHAR(20)  | `open`, `closed`, `merged` (nullable, cached)                            |
| `url`       | VARCHAR(500) | Direct link to the issue/PR on GitHub                                    |

### Achievement

| Field         | Type         | Description                                |
| ------------- | ------------ | ------------------------------------------ |
| `id`          | VARCHAR(50)  | Unique achievement key (e.g. `first_post`) |
| `name`        | VARCHAR(100) | Display name (e.g. "First Steps")          |
| `description` | TEXT         | How to unlock this achievement             |
| `icon`        | VARCHAR(10)  | Emoji icon for the achievement             |
| `xp_reward`   | INTEGER      | XP granted when unlocked                   |

### UserAchievement

| Field            | Type             | Description                             |
| ---------------- | ---------------- | --------------------------------------- |
| `user_id`        | UUID (FK)        | References `User.id`                    |
| `achievement_id` | VARCHAR(50) (FK) | References `Achievement.id`             |
| `unlocked_at`    | TIMESTAMP        | When the achievement was unlocked (UTC) |

**Relationships:**
- `User` 1:N `StatusUpdate`
- `StatusUpdate` 1:N `GitHubLink`
- `User` N:M `Achievement` (via `UserAchievement`)

## Validation Rules

| Field              | Constraint                                                         |
| ------------------ | ------------------------------------------------------------------ |
| `username`         | 3–50 characters, alphanumeric plus underscores and hyphens, unique |
| `email`            | Valid email format, unique                                         |
| `password`         | Minimum 8 characters                                               |
| `display_name`     | 1–100 characters                                                   |
| `message` (status) | 1–500 characters                                                   |
| `category`         | Must be one of: `done`, `in-progress`, `blocked`, `planning`       |

## GitHub Linking

Status update messages are scanned for GitHub references matching the pattern `owner/repo#number` (e.g. `facebook/react#1234`). The parser also recognizes full GitHub URLs:

- `https://github.com/owner/repo/issues/123`
- `https://github.com/owner/repo/pull/456`

These references are:

1. **Parsed** on the backend when a status update is created
2. **Stored** as `GitHubLink` records associated with the status update
3. **Enriched** (optional) — if a `GITHUB_TOKEN` is configured, the backend fetches the issue/PR title, state, and type from the GitHub API and caches it
4. **Rendered** in the frontend as clickable badges showing the repo, number, title, and state with color-coded indicators (green = open, purple = merged, red = closed)

**Example input:**
> Reviewed facebook/react#31019 and started working on our-org/backend#87

**Rendered output:**
> Reviewed [facebook/react#31019 "Act: warn when setState is called ..."] and started working on [our-org/backend#87]

If no GitHub token is provided, links still work — they just show `owner/repo#number` as plain clickable links to `https://github.com/owner/repo/issues/number` without the enriched title and state.

## Gamification

The gamification system encourages consistent participation and engagement.

### XP (Experience Points)

| Action                       | XP                                 |
| ---------------------------- | ---------------------------------- |
| Post a status update         | +10 XP                             |
| Post with a GitHub reference | +5 XP (bonus per unique reference) |
| Maintain a daily streak      | +5 XP per streak day (compounding) |
| Unlock an achievement        | varies (see achievement table)     |

### Streaks

- A **streak** is the number of consecutive calendar days (UTC) a user has posted at least one status update.
- The streak counter is updated whenever a new status is posted.
- If a user misses a day, the streak resets to 0 on their next post.
- The user's `longest_streak` is tracked separately and never resets.

### Achievements

| ID               | Icon | Name          | Condition                                     | XP Reward |
| ---------------- | ---- | ------------- | --------------------------------------------- | --------- |
| `first_post`     | 🎯    | First Steps   | Post your first status update                 | 20 XP     |
| `streak_3`       | 🎩    | Hat Trick     | Reach a 3-day streak                          | 30 XP     |
| `streak_7`       | 🔥    | On Fire       | Reach a 7-day streak                          | 75 XP     |
| `streak_30`      | 💎    | Unstoppable   | Reach a 30-day streak                         | 300 XP    |
| `posts_10`       | 📝    | Regular       | Post 10 status updates total                  | 50 XP     |
| `posts_50`       | ✍️   | Prolific      | Post 50 status updates total                  | 150 XP    |
| `posts_100`      | 🏛️   | Centurion     | Post 100 status updates total                 | 300 XP    |
| `github_first`   | 🔗    | Connected     | Include a GitHub reference for the first time | 25 XP     |
| `github_10`      | 👀    | Code Reviewer | Reference 10 different GitHub issues/PRs      | 100 XP    |
| `all_categories` | 🌈    | Well-Rounded  | Use all 4 categories at least once            | 40 XP     |
| `early_bird`     | 🌅    | Early Bird    | Post before 07:00 UTC                         | 15 XP     |
| `night_owl`      | 🦉    | Night Owl     | Post after 23:00 UTC                          | 15 XP     |

### Leaderboard

The leaderboard ranks all users by total XP. It is accessible at `/leaderboard` and shows:
- Rank, avatar, display name
- Total XP and current level
- Current streak (with fire icon if active today)
- Number of achievements unlocked

**Levels** are derived from XP thresholds:

| Level | XP Required | Title       |
| ----- | ----------- | ----------- |
| 1     | 0           | Newcomer    |
| 2     | 50          | Contributor |
| 3     | 150         | Team Player |
| 4     | 400         | Standout    |
| 5     | 800         | MVP         |
| 6     | 1500        | Legend      |

## API Endpoints

### Auth

| Method | Path                    | Description                  |
| ------ | ----------------------- | ---------------------------- |
| POST   | `/api/v1/auth/register` | Create a new user account    |
| POST   | `/api/v1/auth/login`    | Authenticate and receive JWT |
| POST   | `/api/v1/auth/refresh`  | Refresh an access token      |

#### Examples

**`POST /api/v1/auth/register`** — request:
```json
{
  "username": "alice",
  "email": "alice@example.com",
  "password": "s3cureP@ss",
  "display_name": "Alice"
}
```
Response `201 Created`:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "alice",
  "email": "alice@example.com",
  "display_name": "Alice",
  "avatar_url": null,
  "created_at": "2025-01-15T09:00:00Z"
}
```

**`POST /api/v1/auth/login`** — request:
```json
{
  "username": "alice",
  "password": "s3cureP@ss"
}
```
Response `200 OK`:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```
The refresh token is set as an `httpOnly` cookie.

**`POST /api/v1/auth/refresh`** — request (refresh token sent via cookie):
```json
{}
```
Response `200 OK`:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### Users

| Method | Path                       | Description                   |
| ------ | -------------------------- | ----------------------------- |
| GET    | `/api/v1/users/me`         | Get current user profile      |
| PATCH  | `/api/v1/users/me`         | Update display name or avatar |
| GET    | `/api/v1/users/{username}` | Get public profile of a user  |

#### Examples

**`GET /api/v1/users/me`** — response `200 OK`:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "alice",
  "email": "alice@example.com",
  "display_name": "Alice",
  "avatar_url": null,
  "xp": 120,
  "current_streak": 3,
  "longest_streak": 7,
  "last_post_date": "2025-01-15",
  "created_at": "2025-01-01T09:00:00Z"
}
```

**`PATCH /api/v1/users/me`** — request:
```json
{
  "display_name": "Alice W.",
  "avatar_url": "https://example.com/alice.png"
}
```
Response `200 OK`:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "alice",
  "email": "alice@example.com",
  "display_name": "Alice W.",
  "avatar_url": "https://example.com/alice.png",
  "xp": 120,
  "current_streak": 3,
  "longest_streak": 7,
  "last_post_date": "2025-01-15",
  "created_at": "2025-01-01T09:00:00Z"
}
```

**`GET /api/v1/users/{username}`** — response `200 OK`:
```json
{
  "username": "alice",
  "display_name": "Alice W.",
  "avatar_url": "https://example.com/alice.png",
  "xp": 120,
  "current_streak": 3,
  "longest_streak": 7,
  "created_at": "2025-01-01T09:00:00Z"
}
```

### Status Updates

| Method | Path                    | Description                                |
| ------ | ----------------------- | ------------------------------------------ |
| GET    | `/api/v1/statuses`      | List updates (paginated, filterable)       |
| POST   | `/api/v1/statuses`      | Create a new status update (authenticated) |
| GET    | `/api/v1/statuses/{id}` | Get a single update with GitHub links      |
| PATCH  | `/api/v1/statuses/{id}` | Edit own update (within 15 min)            |
| DELETE | `/api/v1/statuses/{id}` | Delete own update                          |

> **Editing rules:** `PATCH /api/v1/statuses/{id}` is only allowed by the original author and only within 15 minutes of creation. After 15 minutes the endpoint returns `403 Forbidden`.

> **Delete behavior:** `DELETE` performs a hard delete. Associated `GitHubLink` records are cascade-deleted. XP earned from the deleted status is **not** revoked.

#### Query Parameters for `GET /api/v1/statuses`

- `user_id` — filter by user ID
- `username` — filter by username
- `category` — filter by category
- `since` — ISO 8601 timestamp, only return updates after this time
- `limit` — number of results (default: 50, max: 100)
- `offset` — pagination offset

#### Examples

**`POST /api/v1/statuses`** — request:
```json
{
  "message": "Reviewed facebook/react#31019 and fixed our-org/backend#87",
  "category": "done"
}
```
Response `201 Created`:
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440000",
  "user": {
    "username": "alice",
    "display_name": "Alice",
    "avatar_url": null
  },
  "message": "Reviewed facebook/react#31019 and fixed our-org/backend#87",
  "category": "done",
  "github_links": [
    {
      "owner": "facebook",
      "repo": "react",
      "number": 31019,
      "type": "pull_request",
      "title": "Act: warn when setState is called from render",
      "state": "open",
      "url": "https://github.com/facebook/react/pull/31019"
    },
    {
      "owner": "our-org",
      "repo": "backend",
      "number": 87,
      "type": "unknown",
      "title": null,
      "state": null,
      "url": "https://github.com/our-org/backend/issues/87"
    }
  ],
  "created_at": "2025-01-15T09:30:00Z"
}
```

**`GET /api/v1/statuses`** — response `200 OK` (paginated envelope):
```json
{
  "items": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440000",
      "user": { "username": "alice", "display_name": "Alice", "avatar_url": null },
      "message": "Reviewed facebook/react#31019 and fixed our-org/backend#87",
      "category": "done",
      "github_links": [],
      "created_at": "2025-01-15T09:30:00Z"
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

**`GET /api/v1/statuses/{id}`** — response `200 OK`:
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440000",
  "user": {
    "username": "alice",
    "display_name": "Alice",
    "avatar_url": null
  },
  "message": "Reviewed facebook/react#31019 and fixed our-org/backend#87",
  "category": "done",
  "github_links": [
    {
      "owner": "facebook",
      "repo": "react",
      "number": 31019,
      "type": "pull_request",
      "title": "Act: warn when setState is called from render",
      "state": "open",
      "url": "https://github.com/facebook/react/pull/31019"
    }
  ],
  "created_at": "2025-01-15T09:30:00Z"
}
```

**`PATCH /api/v1/statuses/{id}`** — request:
```json
{
  "message": "Updated: reviewed facebook/react#31019",
  "category": "done"
}
```
Response `200 OK`:
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440000",
  "user": {
    "username": "alice",
    "display_name": "Alice",
    "avatar_url": null
  },
  "message": "Updated: reviewed facebook/react#31019",
  "category": "done",
  "github_links": [
    {
      "owner": "facebook",
      "repo": "react",
      "number": 31019,
      "type": "pull_request",
      "title": "Act: warn when setState is called from render",
      "state": "open",
      "url": "https://github.com/facebook/react/pull/31019"
    }
  ],
  "created_at": "2025-01-15T09:30:00Z"
}
```

**`DELETE /api/v1/statuses/{id}`** — response `204 No Content` (empty body).

### Gamification

| Method | Path                                    | Description                                    |
| ------ | --------------------------------------- | ---------------------------------------------- |
| GET    | `/api/v1/leaderboard`                   | Get ranked list of users by XP                 |
| GET    | `/api/v1/users/{username}/achievements` | Get achievements for a user                    |
| GET    | `/api/v1/users/{username}/stats`        | Get user stats (XP, streak, level, post count) |
| GET    | `/api/v1/achievements`                  | List all available achievements                |

#### Examples

**`GET /api/v1/leaderboard`** — response `200 OK`:
```json
[
  {
    "rank": 1,
    "user": {
      "username": "alice",
      "display_name": "Alice",
      "avatar_url": null
    },
    "xp": 320,
    "level": 3,
    "level_title": "Team Player",
    "current_streak": 7,
    "achievements_count": 5
  },
  {
    "rank": 2,
    "user": {
      "username": "bob",
      "display_name": "Bob",
      "avatar_url": "https://example.com/bob.png"
    },
    "xp": 150,
    "level": 3,
    "level_title": "Team Player",
    "current_streak": 0,
    "achievements_count": 3
  }
]
```

**`GET /api/v1/users/{username}/stats`** — response `200 OK`:
```json
{
  "username": "alice",
  "xp": 320,
  "level": 3,
  "level_title": "Team Player",
  "current_streak": 7,
  "longest_streak": 14,
  "total_posts": 42,
  "achievements_unlocked": 5,
  "achievements_total": 12
}
```

**`GET /api/v1/users/{username}/achievements`** — response `200 OK`:
```json
[
  {
    "id": "first_post",
    "name": "First Steps",
    "description": "Post your first status update",
    "icon": "🎯",
    "xp_reward": 20,
    "unlocked_at": "2025-01-01T09:05:00Z"
  },
  {
    "id": "streak_7",
    "name": "On Fire",
    "description": "Reach a 7-day streak",
    "icon": "🔥",
    "xp_reward": 75,
    "unlocked_at": "2025-01-07T10:00:00Z"
  }
]
```

**`GET /api/v1/achievements`** — response `200 OK`:
```json
[
  {
    "id": "first_post",
    "name": "First Steps",
    "description": "Post your first status update",
    "icon": "🎯",
    "xp_reward": 20
  }
]
```

#### Error Responses

All error responses follow a standard format:

**`401 Unauthorized`:**
```json
{
  "detail": "Not authenticated"
}
```

**`404 Not Found`:**
```json
{
  "detail": "Status update not found"
}
```

**`422 Unprocessable Entity`** (validation error):
```json
{
  "detail": [
    {
      "loc": ["body", "message"],
      "msg": "String should have at least 1 character",
      "type": "string_too_short"
    }
  ]
}
```

### System

| Method | Path             | Description             |
| ------ | ---------------- | ----------------------- |
| GET    | `/api/v1/health` | Health check            |
| GET    | `/docs`          | Swagger UI (OpenAPI)    |
| GET    | `/redoc`         | ReDoc API documentation |

### WebSocket

| Path           | Description                            |
| -------------- | -------------------------------------- |
| `/ws/statuses` | Real-time stream of new status updates |

**Protocol:** The client sends a valid JWT as a query parameter (`?token=...`) on connect. On connection, the server sends all updates from the last hour as initial state. After that, every new `POST /api/v1/statuses` triggers a broadcast to all connected WebSocket clients.

**Heartbeat:** The server sends a `ping` frame every 30 seconds. If the server misses 2 consecutive `pong` responses, it closes the connection.

**Reconnection:** The client reconnects with exponential backoff: 1 s → 2 s → 4 s → 8 s → … up to a maximum of 30 s, with unlimited retries. On reconnect, the client sends the timestamp of the last received update so the server can deliver any missed updates.

**Message formats (JSON):**

New status update:
```json
{
  "type": "new_status",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "user": {
      "username": "alice",
      "display_name": "Alice",
      "avatar_url": null
    },
    "message": "Reviewed facebook/react#31019 and fixed our-org/backend#87",
    "category": "done",
    "github_links": [
      {
        "owner": "facebook",
        "repo": "react",
        "number": 31019,
        "type": "pull_request",
        "title": "Act: warn when setState is called from render",
        "state": "open",
        "url": "https://github.com/facebook/react/pull/31019"
      },
      {
        "owner": "our-org",
        "repo": "backend",
        "number": 87,
        "type": "unknown",
        "title": null,
        "state": null,
        "url": "https://github.com/our-org/backend/issues/87"
      }
    ],
    "created_at": "2025-01-15T09:30:00Z"
  }
}
```

Achievement unlocked (sent only to the user who earned it):
```json
{
  "type": "achievement_unlocked",
  "data": {
    "id": "streak_7",
    "name": "On Fire",
    "description": "Reach a 7-day streak",
    "icon": "🔥",
    "xp_reward": 75
  }
}
```

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Node.js 22+ and npm (for local frontend development)
- Python 3.13+ and uv (for local backend development)

### Quick Start (Docker)

```bash
# Clone and start all services
cp .env.example .env
docker compose up -d

# Run database migrations
docker compose exec backend alembic upgrade head

# Open the app
open http://localhost:3000
```

### Local Development

#### Backend

```bash
cd backend

# Create virtual environment and install dependencies
uv sync

# Start PostgreSQL (via Docker)
docker compose up -d db

# Run migrations
uv run alembic upgrade head

# Start the dev server
uv run fastapi dev app/main.py --port 8000
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

#### Seed Data

After running migrations, seed the database with the predefined achievements (and optionally a demo user for local development):

```bash
# Via Makefile
make seed

# Or directly
uv run python -m app.seed
```

This populates the `achievements` table with all 12 achievements defined in the [Achievements](#achievements) section. If the `--demo` flag is passed, it also creates a demo user (`demo` / `demo1234`) for local testing.

## Testing Strategy

This project uses a **three-tier testing approach** to ensure correctness at every level.

### 1. Unit Tests

Verify individual components and functions in isolation with mocked dependencies.

**Backend (pytest):**
```bash
cd backend
uv run pytest tests/unit/ -v
```
- Schema validation (valid/invalid payloads for users, statuses, gamification)
- Service layer logic with mocked database sessions
- GitHub reference parser (`owner/repo#123` extraction, edge cases)
- Gamification engine (XP calculation, streak logic, achievement conditions)
- Password hashing and JWT token creation/validation
- WebSocket manager (connect, disconnect, broadcast)

**Frontend (Jest + React Testing Library):**
```bash
cd frontend
npm test -- --testPathPattern=unit
```
- Component rendering (StatusCard, StatusForm, FilterBar, GitHubRefBadge, LeaderboardTable)
- Hook behavior (useWebSocket reconnection, useAuth token refresh)
- GitHub reference regex matching and rendering
- Form validation and submission
- Achievement toast display logic

### 2. Integration Tests

Test interactions between components with real dependencies (test database, HTTP client).

**Backend (pytest + httpx + testcontainers):**
```bash
cd backend
uv run pytest tests/integration/ -v
```
- User registration and login flow (password hashing, JWT issuance)
- Authenticated status creation with GitHub link extraction
- Full HTTP request/response cycle against test database
- WebSocket connection with JWT authentication
- Database operations (create, read, filter, paginate)
- Gamification triggers (XP award, streak update, achievement unlock on post)
- Error handling (401 unauthorized, 404, 422 validation errors)

**Frontend (Jest + MSW):**
```bash
cd frontend
npm test -- --testPathPattern=integration
```
- Component interaction with mocked API (MSW)
- Status feed rendering with real data flow
- Auth flow (login form -> token storage -> authenticated requests)
- WebSocket mock integration

### 3. End-to-End Tests (Playwright)

Test the complete application from the user's perspective in a real browser.

```bash
# Start the full stack
docker compose -f docker-compose.test.yml up -d

# Run E2E tests
cd frontend
npx playwright test
```

**E2E scenarios:**

- **Auth:** register a new user, log in, see profile
- **Post:** create a status update and verify it appears in the feed
- **Real-time:** open two browser windows with different users, post in one, see it appear in the other
- **GitHub links:** post an update with `owner/repo#123`, verify it renders as a clickable link
- **Filtering:** filter updates by user, category, and verify correct results
- **Gamification:** post first update, verify "First Steps" achievement toast appears
- **Streaks:** post on consecutive days (with mocked clock), verify streak counter increments
- **Leaderboard:** verify users are ranked by XP
- **Responsive:** verify layout on mobile viewport

### Running All Tests

```bash
# Via Makefile
make test            # Run all tests
make test-backend    # Backend unit + integration
make test-frontend   # Frontend unit + integration
make test-e2e        # Playwright E2E tests

# Via Docker Compose
docker compose -f docker-compose.test.yml run --rm test-runner
```

## Development Workflow (LLM-Driven)

This project is designed to be built incrementally using an LLM assistant. The recommended order of implementation follows a strict **test-first approach**: testing infrastructure and linting are established in the very first phase and continuously extended throughout every subsequent phase.

### Quality from Day One

Every phase begins with tests (TDD: RED → GREEN → REFACTOR) and includes linting. The quality toolchain grows incrementally alongside the application code:

| Phase | Quality milestone |
| ----- | --- |
| **Phase 1** | `pytest`, `ruff`, `pyproject.toml` test/lint config — first unit tests run. **GitHub Actions CI:** initial `.github/workflows/ci.yml` with `lint` + `test-backend` jobs |
| **Phase 2** | Auth service unit tests, first integration tests with test DB — CI runs them automatically |
| **Phase 3** | Full API integration test suite, `make test-backend` & `make lint` targets |
| **Phase 4** | Parser unit tests, enrichment integration tests |
| **Phase 5** | Gamification logic unit tests, endpoint integration tests |
| **Phase 6** | WebSocket integration tests |
| **Phase 7** | `jest`, `eslint`, `prettier`, `tsconfig.json` strict mode — first component tests run. **CI erweitert:** `test-frontend` Job hinzugefügt |
| **Phase 8** | Component unit tests, MSW integration tests, `make test-frontend` target |
| **Phase 9** | Playwright E2E tests. **CI finalisiert:** `test-e2e` Job hinzugefügt, alle Checks required für PR-Merge |

> **Rule:** No feature code is merged without corresponding tests. Linters run before every commit (locally via `make lint`, enforced in CI). The GitHub Actions pipeline is created in Phase 1 and grows with every new test layer.

### Phase 1: Backend Foundation
1. Set up the FastAPI project structure with `pyproject.toml` and dependencies
2. **Configure test & lint tooling from the start:**
   - Add `pytest`, `pytest-asyncio`, `pytest-cov`, and `httpx` as dev dependencies
   - Add `ruff` as dev dependency and configure `[tool.ruff]` in `pyproject.toml` (linting + formatting rules)
   - Create `tests/conftest.py` with initial shared fixtures
   - Verify the toolchain: `uv run pytest` passes (zero tests collected), `uv run ruff check .` passes with no errors
3. **Create initial GitHub Actions CI pipeline** (`.github/workflows/ci.yml`):
   - Trigger: push to `main` and pull requests
   - `lint` job: checkout → install `uv` → `uv run ruff check .`
   - `test-backend` job: checkout → install `uv` → start PostgreSQL service container → `uv run pytest --tb=short -q`
   - Verify: push the branch and confirm both jobs pass (green)
4. Configure SQLAlchemy async engine and session management
5. Define the `User` and `StatusUpdate` SQLAlchemy models with relationships
6. Create Alembic migration for the initial schema
7. Implement Pydantic request/response schemas with validation
8. Write unit tests for schemas and model relationships (first RED → GREEN cycle)

### Phase 2: Authentication
1. Write unit tests for password hashing and JWT services (RED)
2. Implement password hashing service (bcrypt) — tests pass (GREEN)
3. Implement JWT creation and validation service — tests pass (GREEN)
4. Write integration tests for registration and login endpoints (RED)
5. Create registration endpoint with email/username uniqueness checks — tests pass (GREEN)
6. Create login endpoint returning access + refresh tokens — tests pass (GREEN)
7. Implement `get_current_user` dependency for protected routes
8. Run `ruff check` and fix any lint issues before committing

### Phase 3: REST API
1. Write integration tests for status CRUD endpoints (RED)
2. Implement status update CRUD service functions — tests pass (GREEN)
3. Create REST API routes with authentication
4. Add pagination and filtering support
5. Write integration tests for user profile endpoints (RED)
6. Add user profile endpoints — tests pass (GREEN)
7. Add health check endpoint with test
8. **Create `Makefile` with `test-backend` and `lint` targets** — establish the `make test-backend` and `make lint` workflow for all subsequent phases

### Phase 4: GitHub Linking
1. Write unit tests for GitHub reference parser (RED)
2. Implement GitHub reference parser (regex for `owner/repo#number`) — tests pass (GREEN)
3. Create `GitHubLink` model and migration
4. Write integration tests for parsing within status creation flow (RED)
5. Integrate parsing into status creation flow — tests pass (GREEN)
6. Add optional GitHub API metadata fetching (title, state, type) with tests
7. Run `make lint` and `make test-backend` — all green before committing

### Phase 5: Gamification
1. Write unit tests for XP calculation, streak tracking, and achievement conditions (RED)
2. Create `Achievement` and `UserAchievement` models and migration
3. Seed the achievements table with all defined achievements
4. Implement XP calculation service — tests pass (GREEN)
5. Implement streak tracking logic — tests pass (GREEN)
6. Implement achievement condition evaluator — tests pass (GREEN)
7. Write integration tests for leaderboard and stats endpoints (RED)
8. Create leaderboard and stats endpoints — tests pass (GREEN)
9. Run `make lint` and `make test-backend` — all green before committing

### Phase 6: Real-Time (WebSocket)
1. Write integration tests for WebSocket connection, auth, and broadcast (RED)
2. Implement WebSocket connection manager with JWT authentication — tests pass (GREEN)
3. Create WebSocket endpoint with initial state delivery — tests pass (GREEN)
4. Hook up POST endpoint to broadcast new updates to all clients
5. Send achievement notifications to individual users on unlock
6. Handle reconnection and error scenarios with tests
7. Run `make lint` and `make test-backend` — all green before committing

### Phase 7: Frontend Foundation
1. Set up Next.js project with TypeScript and Tailwind CSS
2. **Configure test & lint tooling from the start:**
   - Add `jest`, `@testing-library/react`, `@testing-library/jest-dom`, and `msw` as dev dependencies
   - Configure `jest.config.ts` with Next.js SWC transform
   - Add `eslint` (with `eslint-config-next`) and `prettier` — configure rules in `.eslintrc.json` and `.prettierrc`
   - Enable `strict: true` in `tsconfig.json`
   - Verify the toolchain: `npm test` passes (zero tests collected), `npm run lint` passes with no errors
3. **Extend GitHub Actions CI pipeline** — add two new jobs to `.github/workflows/ci.yml`:
   - `lint-frontend` job: checkout → `npm ci` → `npm run lint`
   - `test-frontend` job: checkout → `npm ci` → `npm test -- --ci`
   - Verify: push and confirm all jobs (backend + frontend) pass
4. Define TypeScript interfaces matching backend schemas
5. Create API client module with JWT auth header injection
6. Write unit tests for `useAuth` hook (RED)
7. Implement `useAuth` hook with token storage and refresh — tests pass (GREEN)
8. Write unit tests for login and registration components (RED)
9. Build login and registration pages — tests pass (GREEN)

### Phase 8: Frontend Features
1. Write unit tests for `StatusCard` and `GitHubRefBadge` (RED), then implement (GREEN)
2. Write unit tests for `StatusForm` with validation (RED), then implement (GREEN)
3. Write integration test for `StatusFeed` with MSW (RED)
4. Build `StatusFeed` with data fetching and list rendering — tests pass (GREEN)
5. Write unit tests for `useWebSocket` hook (RED), then implement with auto-reconnection and JWT (GREEN)
6. Add `FilterBar`, `UserAvatar`, and `ConnectionBadge` with unit tests
7. Build user profile page with stats and achievement display
8. Build leaderboard page with unit tests
9. Add `StreakBanner` and `AchievementToast` components with unit tests
10. Write remaining frontend integration tests (auth flow, status feed)
11. **Create `Makefile` target `test-frontend`** — establish the `make test-frontend` workflow
12. Run `npm run lint` and `npm test` — all green before committing

### Phase 9: E2E, CI & Polish
1. Set up Playwright configuration (`playwright.config.ts`, test fixtures)
2. Write E2E test scenarios for auth, posting, real-time, GitHub links, and gamification
3. Add Docker Compose setup for the full stack
4. Create test Docker Compose configuration (`docker-compose.test.yml`)
5. Finalize `Makefile` with all targets (`test`, `test-e2e`, `lint`, `lint-fix`, `build`, `clean`)
6. **Finalize GitHub Actions CI pipeline** — add E2E job to the existing `.github/workflows/ci.yml`:
   - `test-e2e` job: checkout → start full stack via `docker compose -f docker-compose.test.yml up -d` → `npx playwright test` → upload test report as artifact
   - Configure branch protection: all jobs (`lint`, `test-backend`, `lint-frontend`, `test-frontend`, `test-e2e`) must pass before a PR can be merged
   - Final state of the pipeline:
     ```
     push/PR → lint (ruff) ──────────┐
             → lint-frontend (eslint) ┤
             → test-backend (pytest)  ├─→ all must pass
             → test-frontend (jest)   ┤
             → test-e2e (playwright) ─┘
     ```

## Environment Variables

| Variable                    | Default                                                     | Description                                                  |
| --------------------------- | ----------------------------------------------------------- | ------------------------------------------------------------ |
| `DATABASE_URL`              | `postgresql+asyncpg://user:pass@localhost:5432/statusboard` | PostgreSQL connection string                                 |
| `JWT_SECRET`                | (required)                                                  | Secret key for JWT signing                                   |
| `JWT_ACCESS_EXPIRE_MINUTES` | `30`                                                        | Access token expiry                                          |
| `JWT_REFRESH_EXPIRE_DAYS`   | `7`                                                         | Refresh token expiry                                         |
| `CORS_ORIGINS`              | `http://localhost:3000`                                     | Allowed CORS origins                                         |
| `WS_INITIAL_HOURS`          | `1`                                                         | Hours of history sent on WS connect                          |
| `GITHUB_TOKEN`              | (optional)                                                  | GitHub personal access token for enriching issue/PR metadata |
| `LOG_LEVEL`                 | `INFO`                                                      | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`)          |
| `NEXT_PUBLIC_API_URL`       | `http://localhost:8000`                                     | Backend URL for frontend                                     |
| `NEXT_PUBLIC_WS_URL`        | `ws://localhost:8000`                                       | WebSocket URL for frontend                                   |

## CI/CD

The project uses GitHub Actions (`.github/workflows/ci.yml`).

| Trigger                       | Jobs                                                   |
| ----------------------------- | ------------------------------------------------------ |
| Push to `main`, pull requests | `lint` → `test-backend` → `test-frontend` → `test-e2e` |

**Job details:**

| Job             | Description                                                  |
| --------------- | ------------------------------------------------------------ |
| `lint`          | Runs `ruff check` (Python) and `eslint` (TypeScript)         |
| `test-backend`  | `pytest` with a PostgreSQL service container                 |
| `test-frontend` | `jest` (unit + integration)                                  |
| `test-e2e`      | Playwright against a full stack started via `docker compose` |

## Security

| Concern          | Approach                                                              |
| ---------------- | --------------------------------------------------------------------- |
| Password hashing | bcrypt with cost factor 12                                            |
| JWT storage      | Access token held in memory; refresh token in an `httpOnly` cookie    |
| Rate limiting    | 5 requests/minute on `/api/v1/auth/login` and `/api/v1/auth/register` |
| CORS             | Only explicitly configured origins (`CORS_ORIGINS`), no wildcards     |
| SQL injection    | Prevented by SQLAlchemy parameterized queries                         |
| XSS              | React default escaping; message content sanitized server-side         |

## License

Apache License 2.0 — see [LICENSE](LICENSE) for details.
