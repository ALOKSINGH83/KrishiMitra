from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Profile


async def get_or_create(db: AsyncSession, user_id: str) -> Profile:
    profile = await db.scalar(select(Profile).where(Profile.id == user_id))
    if profile:
        return profile
    profile = Profile(id=user_id)
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile
