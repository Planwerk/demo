"""Tests for the health check endpoint and CORS configuration."""

import httpx


async def test_should_return_ok_when_health_checked(client: httpx.AsyncClient) -> None:
    async with client:
        response = await client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_should_include_cors_headers_when_allowed_origin(
    client: httpx.AsyncClient,
) -> None:
    async with client:
        response = await client.options(
            "/api/v1/health",
            headers={
                "origin": "http://localhost:3000",
                "access-control-request-method": "GET",
            },
        )
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert response.headers["access-control-allow-credentials"] == "true"


async def test_should_reject_cors_when_disallowed_origin(
    client: httpx.AsyncClient,
) -> None:
    async with client:
        response = await client.options(
            "/api/v1/health",
            headers={
                "origin": "http://evil.example.com",
                "access-control-request-method": "GET",
            },
        )
    assert "access-control-allow-origin" not in response.headers
