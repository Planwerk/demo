"""Tests for health check endpoint and CORS headers."""

from collections.abc import AsyncIterator

import httpx
import pytest

from app.main import app


@pytest.fixture
async def client() -> AsyncIterator[httpx.AsyncClient]:
    """Async test client against the FastAPI app."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c


async def test_health_returns_200_ok(client: httpx.AsyncClient) -> None:
    """GET /api/v1/health returns 200 with {'status': 'ok'}."""
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


async def test_health_no_auth_required(client: httpx.AsyncClient) -> None:
    """GET /api/v1/health returns 200 without any Authorization header."""
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    assert "authorization" not in resp.request.headers


async def test_health_rejects_post_method(client: httpx.AsyncClient) -> None:
    """POST /api/v1/health returns 405 Method Not Allowed."""
    resp = await client.post("/api/v1/health")
    assert resp.status_code == 405


async def test_cors_headers_present_for_allowed_origin(client: httpx.AsyncClient) -> None:
    """Response includes access-control-allow-origin for the default allowed origin."""
    resp = await client.options(
        "/api/v1/health",
        headers={
            "origin": "http://localhost:3000",
            "access-control-request-method": "GET",
        },
    )
    assert resp.status_code in {200, 204}
    assert resp.headers.get("access-control-allow-origin") == "http://localhost:3000"
    assert resp.headers.get("access-control-allow-credentials") == "true"


async def test_cors_rejects_disallowed_origin(client: httpx.AsyncClient) -> None:
    """Response omits access-control-allow-origin for a non-allowed origin."""
    resp = await client.options(
        "/api/v1/health",
        headers={
            "origin": "http://evil.example.com",
            "access-control-request-method": "GET",
        },
    )
    assert "access-control-allow-origin" not in resp.headers
