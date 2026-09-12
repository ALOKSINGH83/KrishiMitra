from fastapi import APIRouter

from app.api.routes import dashboard, farms, health, insights, profile

api_router=APIRouter()
api_router.include_router(health.router,tags=['system'])
api_router.include_router(profile.router,tags=['profile'])
api_router.include_router(farms.router,tags=['farms'])
api_router.include_router(insights.router,tags=['insights'])
api_router.include_router(dashboard.router,tags=['dashboard'])
