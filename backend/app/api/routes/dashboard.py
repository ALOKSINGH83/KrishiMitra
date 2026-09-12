from fastapi import APIRouter, Depends

from app.core.security import CurrentUser, get_current_user
from app.services import demo

router=APIRouter()
@router.get('/farms/{farm_id}/dashboard')
async def dashboard(farm_id:str,user:CurrentUser=Depends(get_current_user)):
    return {"farm":{"id":farm_id,"name":"Kanpur Wheat Farm","district":"Kanpur Nagar","state":"Uttar Pradesh","area":5,"unit":"acre"},"crop":{"name":"Wheat","growth_stage":"vegetative","area":5},"decision":demo.recommendations()[0],"weather":demo.weather(),"soil":demo.soil(),"risk":demo.risk(),"market":demo.market()}
