from fastapi import APIRouter, Header, HTTPException

from app.agents.task_manager_agent import TaskManagerAgent
from app.core.config import get_settings
from app.models.schemas import UpdateTaskRequest, UpdateTaskStatusRequest


router = APIRouter(prefix="/tasks", tags=["tasks"])


def require_admin(x_admin_token: str | None = Header(default=None)) -> None:
    """Guard destructive routes when ADMIN_TOKEN is configured."""
    settings = get_settings()
    if settings.admin_token and x_admin_token != settings.admin_token:
        raise HTTPException(status_code=401, detail="Invalid or missing X-Admin-Token")


@router.get("")
async def list_tasks() -> dict:
    task_manager = TaskManagerAgent()
    tasks = await task_manager.list_tasks()
    return {"count": len(tasks), "items": tasks}


@router.patch("/{task_id}/status")
async def update_task_status(task_id: str, req: UpdateTaskStatusRequest) -> dict:
    task_manager = TaskManagerAgent()
    updated = await task_manager.update_status(task_id=task_id, status=req.status)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"ok": True, "task_id": task_id, "status": req.status}


@router.patch("/{task_id}")
async def edit_task(task_id: str, req: UpdateTaskRequest, token: None = Header(default=None)) -> dict:
    require_admin(token)
    task_manager = TaskManagerAgent()
    fields = {k: v for k, v in req.model_dump().items() if v is not None}
    updated = await task_manager.update_task(task_id=task_id, fields=fields)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found (or nothing changed)")
    return {"ok": True, "task_id": task_id, "updated_fields": list(fields.keys())}


@router.delete("/{task_id}")
async def delete_task(task_id: str, token: None = Header(default=None)) -> dict:
    require_admin(token)
    task_manager = TaskManagerAgent()
    deleted = await task_manager.delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"ok": True, "task_id": task_id}


@router.post("/demo/accelerate")
async def accelerate_for_demo() -> dict:
    task_manager = TaskManagerAgent()
    updated = await task_manager.force_demo_delay(limit=3)
    return {
        "ok": True,
        "message": "Selected tasks moved into immediate delay window for demo.",
        "tasks_updated": updated,
    }
