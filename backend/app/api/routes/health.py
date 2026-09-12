from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: datetime


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", service="krishimitra-api", timestamp=datetime.now(timezone.utc))


@router.get("/readiness", response_model=HealthResponse)
async def readiness() -> HealthResponse:
    # Database/provider readiness checks are intentionally added when their adapters are introduced.
    return HealthResponse(status="ready", service="krishimitra-api", timestamp=datetime.now(timezone.utc))
