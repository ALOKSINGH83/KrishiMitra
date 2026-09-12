"""Create the deterministic KrishiMitra demo user and core farm data.
Requires SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY and DATABASE_URL in the environment.
"""
import asyncio
import os
from datetime import date, datetime, timedelta, timezone

import httpx
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models import Base, Crop, Farm, Profile, SoilReading

EMAIL = os.getenv("DEMO_EMAIL", "demo@krishimitra.local")
PASSWORD = os.getenv("DEMO_PASSWORD", "KrishiMitraDemo!2026")

async def main():
    url = os.environ["SUPABASE_URL"].rstrip("/")
    service_key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(
            f"{url}/auth/v1/admin/users",
            headers={"Authorization": f"Bearer {service_key}", "apikey": service_key},
            json={"email": EMAIL, "password": PASSWORD, "email_confirm": True},
        )
        if response.status_code == 422 and "already" in response.text.lower():
            users = await client.get(f"{url}/auth/v1/admin/users", headers={"Authorization": f"Bearer {service_key}", "apikey": service_key})
            users.raise_for_status()
            user = next(u for u in users.json().get("users", []) if u.get("email") == EMAIL)
        else:
            response.raise_for_status()
            user = response.json()

    engine = create_async_engine(os.environ["DATABASE_URL"])
    Session = async_sessionmaker(engine, expire_on_commit=False)
    async with Session() as db:
        profile = await db.get(Profile, user["id"])
        if not profile:
            profile = Profile(id=user["id"], display_name="Demo Farmer", preferred_language="en")
            db.add(profile)
        farm = Farm(name="Kanpur Wheat Farm", user_id=user["id"], village="Demo Village", district="Kanpur Nagar", state="Uttar Pradesh", area=5, unit="acre", soil_type="Loam")
        db.add(farm); await db.flush()
        crop = Crop(farm_id=farm.id, crop_code="wheat", name="Wheat", sowing_date=date(2026, 8, 15), growth_stage="vegetative", area=5, status="active")
        db.add(crop)
        soil = SoilReading(farm_id=farm.id, source="sensor", moisture=72, ph=6.8, nitrogen=120, phosphorus=45, potassium=160, temperature_c=23, recorded_at=datetime.now(timezone.utc))
        db.add(soil)
        await db.commit()
    await engine.dispose()
    print(f"Demo user: {EMAIL}")
    print(f"Demo password: {PASSWORD}")
    print("Seeded: Kanpur Wheat Farm, Wheat crop, 72% soil moisture")

if __name__ == "__main__": asyncio.run(main())
