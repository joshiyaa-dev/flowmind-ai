from fastapi import APIRouter

from app.agents.monitoring_agent import MonitoringAgent
from app.core.config import get_settings


router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.post("/run")
async def run_monitoring_cycle() -> dict:
    settings = get_settings()
    monitoring_agent = MonitoringAgent()
    result = await monitoring_agent.run_cycle(settings.inactivity_hours)
    return {"ok": True, "result": result}
