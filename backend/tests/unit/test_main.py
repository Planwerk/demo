"""Tests for the FastAPI application, CORS, and health endpoint."""

from collections.abc import AsyncGenerator

import httpx
import pytest
from httpx import ASGITransport


@pytest.fixture
async def client(
    monkeypatch: pytest.MonkeyPatch,
) -> AsyncGenerator[httpx.AsyncClient]:
    """Create a test client with controlled CORS settings."""
    monkeypatch.setenv("JWT_SECRET", "test-secret")
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000")

    # Clear caches so settings are re-created with test env vars
    from app.config import get_settings

    get_settings.cache_clear()

    from app.main import app

    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as ac:
        yield ac

    get_settings.cache_clear()


class TestHealthEndpoint:
    """Tests for GET /api/v1/health."""

    async def test_health_endpoint_returns_200(
        self, client: httpx.AsyncClient
    ) -> None:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    async def test_health_endpoint_no_auth_required(
        self, client: httpx.AsyncClient
    ) -> None:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200


class TestCORS:
    """Tests for CORS middleware configuration."""

    async def test_cors_allows_configured_origin(
        self, client: httpx.AsyncClient
    ) -> None:
        response = await client.options(
            "/api/v1/health",
            headers={
                "origin": "http://localhost:3000",
                "access-control-request-method": "GET",
            },
        )
        assert response.headers.get("access-control-allow-origin") == (
            "http://localhost:3000"
        )
        assert response.headers.get("access-control-allow-credentials") == "true"

    async def test_cors_blocks_disallowed_origin(
        self, client: httpx.AsyncClient
    ) -> None:
        response = await client.options(
            "/api/v1/health",
            headers={
                "origin": "http://evil.example.com",
                "access-control-request-method": "GET",
            },
        )
        assert "access-control-allow-origin" not in response.headers


class TestDocs:
    """Tests for OpenAPI documentation endpoints."""

    async def test_docs_endpoint_accessible(
        self, client: httpx.AsyncClient
    ) -> None:
        response = await client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    async def test_redoc_endpoint_accessible(
        self, client: httpx.AsyncClient
    ) -> None:
        response = await client.get("/redoc")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
