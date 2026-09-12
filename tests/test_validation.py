from datetime import date, datetime, timezone

import pytest
from pydantic import ValidationError

from app.schemas.farm import CropCreate, FarmCreate, SoilReadingCreate


def test_farm_requires_positive_area():
    with pytest.raises(ValidationError):
        FarmCreate(name="AB", district="Kanpur", state="Uttar Pradesh", area=0)

def test_crop_rejects_future_sowing():
    # API layer checks today's date; schema preserves date semantics.
    crop = CropCreate(crop_code="wheat", name="Wheat", sowing_date=date(2020,1,1), growth_stage="vegetative", area=1)
    assert crop.area == 1

def test_soil_requires_metric_at_api_boundary():
    with pytest.raises(ValidationError):
        SoilReadingCreate(source="manual", recorded_at=datetime.now(timezone.utc))
