"""Tests for health check endpoint and CORS headers."""

from collections.abc import AsyncGenerator

import httpx
import pytest


@pytest.fixture
async def client() -> AsyncGenerator[httpx.AsyncClient]:
    from app.main import app

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


async def test_should_return_ok_status_when_health_checked(client: httpx.AsyncClient) -> None:
    response = await client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_should_respond_without_auth_when_no_middleware_configured(
    client: httpx.AsyncClient,
) -> None:
    """Establishes intent: health endpoint must remain accessible when auth middleware is added."""
    response = await client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_should_include_cors_headers_when_allowed_origin_sent(
    client: httpx.AsyncClient,
) -> None:
    response = await client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
    assert response.headers.get("access-control-allow-credentials") == "true"


async def test_should_not_include_cors_headers_when_disallowed_origin_sent(
    client: httpx.AsyncClient,
) -> None:
    response = await client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://evil.com",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers
