"""Unit tests for the health check endpoint."""

import httpx


class TestHealthReturns200Ok:
    """GET /api/v1/health returns status 200 and body {'status': 'ok'}."""

    async def test_health_returns_200_ok(self, async_client: httpx.AsyncClient) -> None:
        response = await async_client.get("/api/v1/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestHealthNoAuthRequired:
    """GET /api/v1/health returns 200 without any Authorization header."""

    async def test_health_no_auth_required(self, async_client: httpx.AsyncClient) -> None:
        response = await async_client.get("/api/v1/health")

        assert "Authorization" not in response.request.headers
        assert response.status_code == 200


class TestCorsHeadersPresentForAllowedOrigin:
    """Response includes access-control-allow-origin for http://localhost:3000."""

    async def test_cors_headers_present_for_allowed_origin(
        self, async_client: httpx.AsyncClient
    ) -> None:
        response = await async_client.options(
            "/api/v1/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )

        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
