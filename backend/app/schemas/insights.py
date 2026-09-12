from datetime import datetime

from pydantic import BaseModel, Field


class WeatherDay(BaseModel):
    date: str
    temp_min_c: float
    temp_max_c: float
    rain_probability: int = Field(ge=0, le=100)
    rainfall_mm: float
    condition: str

class WeatherResponse(BaseModel):
    location: str
    observed_at: datetime
    source: str
    stale: bool
    current_temp_c: float
    rain_probability: int
    humidity: int
    wind_kph: float
    forecast: list[WeatherDay]
    impact: str

class SoilSummary(BaseModel):
    recorded_at: datetime | None
    moisture: float | None
    ph: float | None
    nitrogen: float | None
    phosphorus: float | None
    potassium: float | None
    temperature_c: float | None
    freshness: str
    moisture_status: str

class RiskFactor(BaseModel):
    factor: str
    effect: str
    score: float = Field(ge=0, le=1)

class RiskResponse(BaseModel):
    overall_score: float = Field(ge=0, le=1)
    disease_score: float = Field(ge=0, le=1)
    pest_score: float = Field(ge=0, le=1)
    weather_score: float = Field(ge=0, le=1)
    confidence: str
    factors: list[RiskFactor]
    disclaimer: str

class Recommendation(BaseModel):
    id: str
    title: str
    priority: str
    why: str
    evidence: list[str]
    valid_until: datetime
    state: str

class MarketPoint(BaseModel):
    date: str
    price: float
    unit: str
    source: str

class MarketResponse(BaseModel):
    commodity: str
    market: str
    unit: str
    history: list[MarketPoint]
    forecast_low: float
    forecast_high: float
    trend: str
    signal: str
    confidence: str
    disclaimer: str

class AdvisorRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    language: str = "en"
    idempotency_key: str | None = None

class AdvisorSource(BaseModel):
    title: str
    source_id: str

class AdvisorResponse(BaseModel):
    answer: str
    sources: list[AdvisorSource]
    safety_note: str | None = None
