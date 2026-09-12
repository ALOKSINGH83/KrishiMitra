from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class FarmCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    village: str | None = Field(default=None, max_length=120)
    district: str = Field(min_length=2, max_length=120)
    state: str = Field(min_length=2, max_length=120)
    pincode: str | None = Field(default=None, max_length=10)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    area: Decimal = Field(gt=0)
    unit: Literal["acre", "hectare"] = "acre"
    soil_type: str | None = Field(default=None, max_length=80)

class FarmUpdate(BaseModel):
    """All fields optional – safe for PATCH requests."""
    name: str | None = Field(default=None, min_length=2, max_length=80)
    village: str | None = Field(default=None, max_length=120)
    district: str | None = Field(default=None, min_length=2, max_length=120)
    state: str | None = Field(default=None, min_length=2, max_length=120)
    pincode: str | None = Field(default=None, max_length=10)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    area: Decimal | None = Field(default=None, gt=0)
    unit: Literal["acre", "hectare"] | None = None
    soil_type: str | None = Field(default=None, max_length=80)


class FarmResponse(FarmCreate):
    id: str
    user_id: str
    archived_at: datetime | None = None

class CropCreate(BaseModel):
    crop_code: str = Field(min_length=2, max_length=40)
    name: str = Field(min_length=2, max_length=80)
    variety: str | None = Field(default=None, max_length=80)
    sowing_date: date
    growth_stage: Literal["sowing","germination","vegetative","flowering","fruiting","maturity","harvested"]
    expected_harvest_date: date | None = None
    area: Decimal = Field(gt=0)

    @model_validator(mode="after")
    def dates_valid(self):
        if self.expected_harvest_date and self.expected_harvest_date < self.sowing_date:
            raise ValueError("Harvest date cannot be before sowing date")
        return self

class CropResponse(CropCreate):
    id: str
    farm_id: str
    status: Literal["active", "archived"] = "active"

class SoilReadingCreate(BaseModel):
    source: Literal["manual","sensor"] = "manual"
    moisture: float | None = Field(default=None, ge=0, le=100)
    ph: float | None = Field(default=None, ge=0, le=14)
    nitrogen: float | None = Field(default=None, ge=0, le=500)
    phosphorus: float | None = Field(default=None, ge=0, le=500)
    potassium: float | None = Field(default=None, ge=0, le=500)
    temperature_c: float | None = Field(default=None, ge=-10, le=70)
    recorded_at: datetime
    notes: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def has_metric_and_timestamp(self):
        if all(v is None for v in (self.moisture, self.ph, self.nitrogen, self.phosphorus, self.potassium, self.temperature_c)):
            raise ValueError("At least one soil metric is required")
        if self.recorded_at.tzinfo is None:
            raise ValueError("recordedAt must include timezone")
        if self.recorded_at > datetime.now(timezone.utc) + timedelta(minutes=15):
            raise ValueError("recordedAt cannot be more than 15 minutes in the future")
        return self

class SoilReadingResponse(SoilReadingCreate):
    id: str
    farm_id: str
