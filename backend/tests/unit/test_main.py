"""Tests for app.main module."""

from httpx import AsyncClient


async def test_health_endpoint_returns_200(async_client: AsyncClient) -> None:
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_cors_allows_configured_origin(async_client: AsyncClient) -> None:
    response = await async_client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"


async def test_cors_blocks_disallowed_origin(async_client: AsyncClient) -> None:
    response = await async_client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://evil.example.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.headers.get("access-control-allow-origin") != "http://evil.example.com"


async def test_docs_endpoint_accessible(async_client: AsyncClient) -> None:
    response = await async_client.get("/docs")
    assert response.status_code == 200


async def test_redoc_endpoint_accessible(async_client: AsyncClient) -> None:
    response = await async_client.get("/redoc")
    assert response.status_code == 200
