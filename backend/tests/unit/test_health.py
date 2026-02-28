"""Tests for health check endpoint and CORS headers."""

import httpx
import pytest

from app.main import app


@pytest.fixture
def client() -> httpx.AsyncClient:
    """Async test client against the FastAPI app."""
    transport = httpx.ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://testserver")


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


async def test_cors_headers_present_for_allowed_origin(client: httpx.AsyncClient) -> None:
    """Response includes access-control-allow-origin for the default allowed origin."""
    resp = await client.options(
        "/api/v1/health",
        headers={
            "origin": "http://localhost:3000",
            "access-control-request-method": "GET",
        },
    )
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
    assert resp.headers.get("access-control-allow-origin") != "http://evil.example.com"
