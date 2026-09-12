from fastapi import APIRouter, Depends, Header, HTTPException

from app.core.security import CurrentUser, get_current_user
from app.schemas.insights import (
    AdvisorRequest,
    AdvisorResponse,
    MarketResponse,
    Recommendation,
    RiskResponse,
    SoilSummary,
    WeatherResponse,
)
from app.services import demo

router = APIRouter()


@router.get("/farms/{farm_id}/weather", response_model=WeatherResponse)
async def weather(farm_id: str, user: CurrentUser = Depends(get_current_user)):
    return demo.weather()


@router.get("/farms/{farm_id}/soil-summary", response_model=SoilSummary)
async def soil_summary(farm_id: str, user: CurrentUser = Depends(get_current_user)):
    return demo.soil()


@router.get("/farms/{farm_id}/risk", response_model=RiskResponse)
async def risk(farm_id: str, user: CurrentUser = Depends(get_current_user)):
    return demo.risk()


@router.get("/farms/{farm_id}/recommendations", response_model=list[Recommendation])
async def recs(farm_id: str, user: CurrentUser = Depends(get_current_user)):
    return demo.recommendations()


@router.patch("/recommendations/{recommendation_id}/state", response_model=Recommendation)
async def rec_state(
    recommendation_id: str,
    state: str,
    user: CurrentUser = Depends(get_current_user),
):
    allowed = {"acknowledged", "completed", "dismissed"}
    if state not in allowed:
        raise HTTPException(422, "Invalid recommendation state")
    items = demo.recommendations()
    item = next((x for x in items if x["id"] == recommendation_id), None)
    if not item:
        raise HTTPException(404, "Recommendation not found")
    item["state"] = state
    return item


@router.get("/farms/{farm_id}/market", response_model=MarketResponse)
async def market(farm_id: str, user: CurrentUser = Depends(get_current_user)):
    return demo.market()


@router.post("/farms/{farm_id}/advisor", response_model=AdvisorResponse)
async def advisor(
    farm_id: str,
    payload: AdvisorRequest,
    user: CurrentUser = Depends(get_current_user),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):
    return demo.advisor(payload.message, payload.language)
