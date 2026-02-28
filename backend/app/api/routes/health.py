"""Health check endpoint."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1")


@router.get("/health")
async def health() -> dict[str, str]:
    """Return application health status."""
    return {"status": "ok"}
