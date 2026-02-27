"""Tests for health check endpoint and CORS headers (REQ-005, REQ-006)."""

from collections.abc import AsyncGenerator

import httpx
import pytest
from httpx import ASGITransport

from app.main import app


@pytest.fixture
async def client() -> AsyncGenerator[httpx.AsyncClient]:
    """Async test client against the FastAPI app."""
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


async def test_health_returns_200_ok(client: httpx.AsyncClient) -> None:
    """GET /api/v1/health returns 200 with {'status': 'ok'}."""
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


async def test_health_no_auth_required(client: httpx.AsyncClient) -> None:
    """Health check requires no authentication headers."""
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200


async def test_cors_headers_present_for_allowed_origin(
    client: httpx.AsyncClient,
) -> None:
    """CORS headers present for allowed origin on preflight."""
    resp = await client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert (
        resp.headers.get("access-control-allow-origin")
        == "http://localhost:3000"
    )
    assert resp.headers.get("access-control-allow-credentials") == "true"


async def test_cors_headers_present_for_allowed_origin_on_get(
    client: httpx.AsyncClient,
) -> None:
    """CORS headers present for allowed origin on a normal GET request."""
    resp = await client.get(
        "/api/v1/health",
        headers={
            "Origin": "http://localhost:3000",
        },
    )
    assert (
        resp.headers.get("access-control-allow-origin")
        == "http://localhost:3000"
    )
    assert resp.headers.get("access-control-allow-credentials") == "true"


async def test_cors_disallowed_origin_blocked(
    client: httpx.AsyncClient,
) -> None:
    """Requests from non-whitelisted origins do not receive CORS headers."""
    resp = await client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://evil.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert "access-control-allow-origin" not in resp.headers
