from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Crop, Farm, SoilReading


async def list_farms(db: AsyncSession, user_id: str) -> list[Farm]:
    result = await db.scalars(select(Farm).where(Farm.user_id == user_id, Farm.archived_at.is_(None)).order_by(Farm.name))
    return list(result)

async def get_owned_farm(db: AsyncSession, farm_id: str, user_id: str) -> Farm | None:
    return await db.scalar(select(Farm).where(Farm.id == farm_id, Farm.user_id == user_id, Farm.archived_at.is_(None)))

async def archive_farm(db: AsyncSession, farm: Farm) -> None:
    farm.archived_at = datetime.now(timezone.utc)
    await db.commit()

async def list_crops(db: AsyncSession, farm_id: str) -> list[Crop]:
    result = await db.scalars(select(Crop).where(Crop.farm_id == farm_id, Crop.status == "active").order_by(Crop.sowing_date.desc()))
    return list(result)

async def list_soil(db: AsyncSession, farm_id: str) -> list[SoilReading]:
    result = await db.scalars(select(SoilReading).where(SoilReading.farm_id == farm_id).order_by(SoilReading.recorded_at.desc()))
    return list(result)
