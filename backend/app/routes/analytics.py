from datetime import datetime, timezone

from fastapi import APIRouter

from app.agents.task_manager_agent import TaskManagerAgent


router = APIRouter(prefix="/analytics", tags=["analytics"])


def _as_utc(value):
    if not value:
        return None
    if isinstance(value, datetime):
        dt = value
    else:
        try:
            dt = datetime.fromisoformat(str(value))
        except Exception:
            return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


@router.get("")
async def analytics_summary() -> dict:
    task_manager = TaskManagerAgent()
    tasks = await task_manager.list_tasks()
    logs = await task_manager.list_logs()

    total = len(tasks)
    completed = len([t for t in tasks if t.get("status") == "completed"])
    delayed = len([t for t in tasks if t.get("status") == "delayed"])
    pending = len([t for t in tasks if t.get("status") == "pending"])

    now = datetime.now(timezone.utc)
    overdue = len(
        [
            t
            for t in tasks
            if t.get("status") != "completed"
            and (_as_utc(t.get("simulated_deadline_at") or t.get("deadline")) is not None)
            and (_as_utc(t.get("simulated_deadline_at") or t.get("deadline")) < now)
        ]
    )

    reminder_events = len([l for l in logs if l.get("action") == "reminder_sent"])
    escalation_events = len([l for l in logs if l.get("action") == "escalation_triggered"])
    delays_prevented = len(
        [
            t
            for t in tasks
            if t.get("status") == "completed" and (t.get("reminder_count", 0) > 0 or t.get("escalated"))
        ]
    )
    time_saved_hours = round((reminder_events * 0.25) + (escalation_events * 0.6) + (completed * 0.5), 1)

    return {
        "total_tasks": total,
        "completed_tasks": completed,
        "pending_tasks": pending,
        "delayed_tasks": delayed,
        "overdue_tasks": overdue,
        "completion_rate": round((completed / total) * 100, 2) if total else 0,
        "reminders_sent": reminder_events,
        "escalations_triggered": escalation_events,
        "delays_prevented": delays_prevented,
        "time_saved_hours": time_saved_hours,
    }
