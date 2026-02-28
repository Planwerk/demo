"""API v1 router definition and route registrations."""

from fastapi import APIRouter

api_router = APIRouter(prefix="/api/v1")


@api_router.get("/health")
async def health_check() -> dict[str, str]:
    """Return service health status."""
    return {"status": "ok"}
