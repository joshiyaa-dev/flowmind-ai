from fastapi import APIRouter

from app.agents.task_manager_agent import TaskManagerAgent


router = APIRouter(prefix="/logs", tags=["logs"])


@router.get("")
async def list_logs() -> dict:
    task_manager = TaskManagerAgent()
    logs = await task_manager.list_logs()
    return {"count": len(logs), "items": logs}
