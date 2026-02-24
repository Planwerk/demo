# Team Statusboard

A real-time team status update application built with FastAPI (Python 3.13, async SQLAlchemy, Pydantic v2) and
Next.js 15 (React 19, TypeScript, Tailwind CSS). Team members post short status updates that appear in real time
via WebSockets, are persisted in PostgreSQL, and can reference GitHub Issues/PRs as rich links. A gamification
layer with XP, streaks, achievements, and a leaderboard keeps the team engaged. The project is designed for
LLM-driven incremental development with three-tier testing (pytest, Jest, Playwright).

## Phase 1: Backend Foundation

Set up the FastAPI project structure, database layer, ORM models, and Pydantic schemas.

- **S01: Project Scaffold & Database Layer** [high]
  `backend/` with `pyproject.toml`, `app/main.py` (FastAPI + CORS), `app/config.py` (pydantic-settings, all env vars), `app/database.py` (async engine, session, `get_db()` dependency).
- **S02: ORM Models & Migration** [high] (depends on: S01)
  User and StatusUpdate models with all fields per data model, relationships. Alembic async config, initial migration.
- **S03: Pydantic Schemas & Unit Tests** [high] (depends on: S02)
  Request/response schemas (UserCreate, StatusCreate, TokenResponse, PaginatedStatusResponse) with validation rules. `tests/conftest.py` with shared fixtures, `tests/unit/test_schemas.py`.

## Phase 2: Authentication

Implement password hashing, JWT tokens, and auth endpoints (register, login, refresh).

- **S04: Auth Services** [high] (depends on: S01)
  `app/services/auth.py` — bcrypt hash/verify (cost 12), JWT create/decode (HS256, access 30 min, refresh 7 days).
- **S05: Auth Endpoints & Dependency** [high] (depends on: S02, S03, S04)
  `POST /register` (uniqueness check, 201), `POST /login` (access token in body, refresh as httpOnly cookie, rate limit 5/min), `POST /refresh`. `get_current_user` dependency in `app/api/deps.py`.
- **S06: Auth Tests** [high] (depends on: S05)
  Unit tests for hash/JWT services, integration tests for register/login/refresh flows and 401 on protected routes.

## Phase 3: REST API

Implement status CRUD, pagination, filtering, user profiles, health check, and structured logging.

- **S07: Status CRUD** [high] (depends on: S02, S05)
  Service layer (`create`, `list`, `get`, `update`, `delete`) and REST routes: POST (201), GET list (paginated envelope), GET single, PATCH (author-only, 15-min window), DELETE (hard, 204). Query params: user_id, username, category, since, limit, offset.
- **S08: User Profiles, Health & Logging** [medium] (depends on: S05)
  `GET /users/me`, `PATCH /users/me`, `GET /users/{username}`. Health check, `/docs`, `/redoc`. Structured JSON logging via structlog with request-ID middleware.
- **S09: REST API Integration Tests** [high] (depends on: S07, S08)
  Full CRUD flows, pagination, filtering, edit-window enforcement, user profile operations.

## Phase 4: GitHub Linking

Implement GitHub reference parsing, the GitHubLink model, and optional metadata enrichment.

- **S10: Parser & Model** [high] (depends on: S02)
  `parse_github_references(text)` extracting from `owner/repo#number` and full GitHub URLs. GitHubLink model with CASCADE delete, Alembic migration.
- **S11: Integration & Enrichment** [high] (depends on: S07, S10)
  Parse message on create/update, persist GitHubLink rows, include in StatusResponse. Optional metadata fetch from GitHub API when `GITHUB_TOKEN` is set (best-effort, non-blocking).
- **S12: GitHub Linking Tests** [high] (depends on: S11)
  Unit tests for parser (patterns, deduplication, edge cases), integration tests for status creation with refs.

## Phase 5: Gamification

Implement XP, streaks, achievements, seeding, leaderboard, and stats endpoints.

- **S13: Models & Seeding** [high] (depends on: S02)
  Achievement and UserAchievement models (N:M), migration. `app/seed.py` upserting all 12 achievements with icons/XP, `--demo` flag. Wired as `make seed`.
- **S14: XP, Streaks & Achievement Engine** [high] (depends on: S07, S13)
  `app/services/gamification.py` — XP calculation (+10 base, +5/ref, +5×streak), streak tracking (consecutive days), achievement condition evaluator (all 12 rules). Hooked into `create_status` pipeline.
- **S15: Endpoints & Schemas** [high] (depends on: S14)
  `GET /leaderboard`, `GET /users/{username}/stats`, `GET /users/{username}/achievements`, `GET /achievements`. Response schemas in `app/schemas/gamification.py`.
- **S16: Gamification Tests** [high] (depends on: S14, S15)
  Unit tests for XP/streak/achievement logic, integration tests for endpoints and achievement triggering on post.

## Phase 6: Real-Time (WebSocket)

Implement WebSocket connection manager, broadcast, achievement notifications, and heartbeat.

- **S17: Connection Manager & Endpoint** [high] (depends on: S05)
  `ConnectionManager` (connect with JWT, disconnect, broadcast, send_personal). `ws /ws/statuses` with initial state delivery (last `WS_INITIAL_HOURS`).
- **S18: Broadcast & Notifications** [high] (depends on: S07, S14, S17)
  Broadcast `new_status` to all clients on POST. Send `achievement_unlocked` only to earning user. Server ping every 30 s, close after 2 missed pongs, `?last_received=` for reconnect.
- **S19: WebSocket Tests** [high] (depends on: S18)
  Auth, initial state, broadcast receipt, achievement delivery, invalid token rejection.

## Phase 7: Frontend Foundation

Set up the Next.js project, API client, auth state, and login/registration pages.

- **S20: Project Scaffold & API Client** [high]
  `frontend/` via create-next-app (App Router, TypeScript, Tailwind). `src/lib/types.ts` mirroring backend schemas. `src/lib/api.ts` with Bearer injection, auto-refresh on 401, typed functions.
- **S21: Auth State & Pages** [high] (depends on: S20)
  `useAuth` hook + `AuthProvider` Context (token in memory, silent refresh). Login and registration pages with client-side validation, server error display, redirect.
- **S22: Auth Component Tests** [high] (depends on: S21)
  Jest + RTL tests for login/registration forms.

## Phase 8: Frontend Features

Build the status feed, components, WebSocket integration, profile, and leaderboard pages.

- **S23: Core Components** [high] (depends on: S20)
  StatusCard (avatar, message, category tag, timestamp, GitHubRefBadge list), StatusForm (textarea with counter, category dropdown), FilterBar, UserAvatar, ConnectionBadge.
- **S24: StatusFeed & WebSocket** [high] (depends on: S23)
  Paginated fetch, infinite scroll, `useWebSocket` hook (exponential backoff reconnect, `last_received`), live prepend of new statuses. StreakBanner, AchievementToast (auto-dismiss 5 s).
- **S25: Profile & Leaderboard Pages** [high] (depends on: S24)
  `profile/[username]/page.tsx` (stats, achievements grid, recent statuses). `leaderboard/page.tsx` (ranked table with XP, level, streak).
- **S26: Frontend Tests** [high] (depends on: S24)
  Unit tests (StatusCard, StatusForm, GitHubRefBadge, FilterBar, gamification components). Integration tests (StatusFeed with MSW, auth-flow).

## Phase 9: E2E, CI & Polish

Set up Docker, Makefile, Playwright E2E tests, and CI pipeline.

- **S27: Docker & Makefile** [high] (depends on: S01, S20)
  `docker-compose.yml` (db, backend, frontend), `docker-compose.test.yml`, `.env.example`. Multi-stage Dockerfiles (non-root). Makefile with all targets per README.
- **S28: Playwright E2E Tests** [high] (depends on: S27)
  `playwright.config.ts`, auth fixtures. Test scenarios: auth, posting, real-time (two contexts), GitHub links, gamification, edit/delete.
- **S29: CI Pipeline** [medium] (depends on: S27)
  `.github/workflows/ci.yml` — lint (ruff + eslint), test-backend (PostgreSQL service), test-frontend (jest), test-e2e (playwright + docker compose).
