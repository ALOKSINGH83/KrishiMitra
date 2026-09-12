from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import CurrentUser, get_current_user
from app.db.session import get_db
from app.repositories.profiles import get_or_create
from app.schemas.profile import ProfileResponse, ProfileUpdate

router = APIRouter(prefix="/me")

@router.get("", response_model=ProfileResponse)
async def get_me(user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await get_or_create(db, user.id)

@router.patch("", response_model=ProfileResponse)
async def update_me(payload: ProfileUpdate, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    profile = await get_or_create(db, user.id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, key, value)
    await db.commit()
    await db.refresh(profile)
    return profile
