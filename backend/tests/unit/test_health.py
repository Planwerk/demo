"""Tests for health check endpoint and CORS headers (REQ-005, REQ-006)."""

from collections.abc import AsyncGenerator

import httpx
import pytest


@pytest.fixture
async def client() -> AsyncGenerator[httpx.AsyncClient]:
    """Yield an async test client for the FastAPI app."""
    from app.main import app

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c


async def test_should_return_200_ok_when_health_checked(client: httpx.AsyncClient) -> None:
    """GET /api/v1/health returns 200 with {'status': 'ok'}."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_should_return_200_when_no_auth_header_provided(client: httpx.AsyncClient) -> None:
    """Health check works without any auth headers."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200


async def test_should_include_cors_headers_when_allowed(client: httpx.AsyncClient) -> None:
    """CORS headers present for allowed origin on preflight request."""
    response = await client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
    assert response.headers.get("access-control-allow-credentials") == "true"


async def test_should_omit_cors_headers_when_disallowed(client: httpx.AsyncClient) -> None:
    """CORS headers absent for a disallowed origin on preflight request."""
    response = await client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://evil.example.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.headers.get("access-control-allow-origin") is None
