from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import CurrentUser, get_current_user
from app.db.session import get_db
from app.models import Crop, Farm, IdempotencyKey, SoilReading
from app.repositories.farms import (
    archive_farm,
    get_owned_farm,
    list_crops,
    list_farms,
    list_soil,
)
from app.repositories.profiles import get_or_create
from app.schemas.farm import (
    CropCreate,
    CropResponse,
    FarmCreate,
    FarmResponse,
    FarmUpdate,
    SoilReadingCreate,
    SoilReadingResponse,
)

router = APIRouter(prefix="/farms")


async def owned(db: AsyncSession, farm_id: str, user_id: str) -> Farm:
    farm = await get_owned_farm(db, farm_id, user_id)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found or unavailable")
    return farm


@router.get("", response_model=list[FarmResponse])
async def get_farms(user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await list_farms(db, user.id)


@router.post("", response_model=FarmResponse, status_code=status.HTTP_201_CREATED)
async def create_farm(payload: FarmCreate, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await get_or_create(db, user.id)
    farm = Farm(user_id=user.id, **payload.model_dump())
    db.add(farm)
    await db.commit()
    await db.refresh(farm)
    return farm


@router.get("/{farm_id}", response_model=FarmResponse)
async def get_farm(farm_id: str, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await owned(db, farm_id, user.id)


@router.patch("/{farm_id}", response_model=FarmResponse)
async def update_farm(
    farm_id: str,
    payload: FarmUpdate,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    farm = await owned(db, farm_id, user.id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(farm, key, value)
    await db.commit()
    await db.refresh(farm)
    return farm


@router.delete("/{farm_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_farm(farm_id: str, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    farm = await owned(db, farm_id, user.id)
    await archive_farm(db, farm)


@router.get("/{farm_id}/crops", response_model=list[CropResponse])
async def get_crops(farm_id: str, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await owned(db, farm_id, user.id)
    return await list_crops(db, farm_id)


@router.post("/{farm_id}/crops", response_model=CropResponse, status_code=status.HTTP_201_CREATED)
async def create_crop(
    farm_id: str,
    payload: CropCreate,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    farm = await owned(db, farm_id, user.id)
    today = datetime.now(timezone.utc).date()
    if payload.area > farm.area:
        raise HTTPException(422, "Crop area cannot exceed farm area")
    if payload.sowing_date > today:
        raise HTTPException(422, "Sowing date cannot be in the future")
    if payload.expected_harvest_date and payload.expected_harvest_date < payload.sowing_date:
        raise HTTPException(422, "Harvest date cannot be before sowing date")
    crop = Crop(farm_id=farm_id, **payload.model_dump())
    db.add(crop)
    await db.commit()
    await db.refresh(crop)
    return crop


@router.patch("/crops/{crop_id}", response_model=CropResponse)
async def update_crop(
    crop_id: str,
    payload: CropCreate,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    crop = await db.get(Crop, crop_id)
    if not crop:
        raise HTTPException(404, "Crop not found or unavailable")
    # Verify ownership via the farm (single call — no duplicate round-trip)
    farm = await owned(db, crop.farm_id, user.id)
    if payload.area > farm.area:
        raise HTTPException(422, "Crop area cannot exceed farm area")
    for key, value in payload.model_dump().items():
        setattr(crop, key, value)
    await db.commit()
    await db.refresh(crop)
    return crop


@router.get("/{farm_id}/soil-readings", response_model=list[SoilReadingResponse])
async def get_soil(farm_id: str, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await owned(db, farm_id, user.id)
    return await list_soil(db, farm_id)


@router.post("/{farm_id}/soil-readings", response_model=SoilReadingResponse, status_code=status.HTTP_201_CREATED)
async def create_soil(
    farm_id: str,
    payload: SoilReadingCreate,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):
    await owned(db, farm_id, user.id)
    if not idempotency_key:
        raise HTTPException(400, "Idempotency-Key is required")
    existing = await db.scalar(
        select(IdempotencyKey).where(
            IdempotencyKey.user_id == user.id,
            IdempotencyKey.key == idempotency_key,
            IdempotencyKey.operation == "soil-create",
        )
    )
    if existing and existing.response_id:
        previous = await db.get(SoilReading, existing.response_id)
        if previous:
            return previous
    if payload.recorded_at.tzinfo is None:
        raise HTTPException(422, "recordedAt must include timezone")
    if payload.recorded_at > datetime.now(timezone.utc).replace(second=0, microsecond=0) + timedelta(minutes=15):
        raise HTTPException(422, "recordedAt cannot be more than 15 minutes in the future")
    if all(v is None for v in (payload.moisture, payload.ph, payload.nitrogen, payload.phosphorus, payload.potassium, payload.temperature_c)):
        raise HTTPException(422, "At least one soil metric is required")
    reading = SoilReading(farm_id=farm_id, **payload.model_dump())
    db.add(reading)
    await db.flush()
    db.add(IdempotencyKey(user_id=user.id, key=idempotency_key, operation="soil-create", response_id=reading.id))
    await db.commit()
    await db.refresh(reading)
    return reading
