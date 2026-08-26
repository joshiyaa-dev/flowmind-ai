from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.core.config import get_settings


class PlanningAgent:
    @staticmethod
    def _safe_parse_deadline(raw_deadline: str, now: datetime) -> datetime:
        try:
            deadline = datetime.fromisoformat(str(raw_deadline))
            if deadline.tzinfo is None:
                deadline = deadline.replace(tzinfo=timezone.utc)
            return deadline
        except Exception:
            return now + timedelta(days=7)

    @staticmethod
    def plan(extracted_tasks: list[dict], meeting_id: str) -> list[dict]:
        """Convert extracted tasks into database-ready workflow tasks."""
        planned: list[dict] = []
        now = datetime.now(timezone.utc)
        settings = get_settings()

        for item in extracted_tasks:
            deadline = PlanningAgent._safe_parse_deadline(item.get("deadline", ""), now)

            days_to_deadline = max(1, (deadline.date() - now.date()).days)
            planned.append(
                {
                    "task_id": str(uuid4()),
                    "task": item["task"],
                    "owner": item["owner"],
                    "deadline": item["deadline"],
                    "simulated_deadline_at": now.replace(microsecond=0)
                    + timedelta(seconds=days_to_deadline * settings.demo_day_seconds),
                    "status": "pending",
                    "created_at": now,
                    "updated_at": now,
                    "last_activity_at": now,
                    "reminder_count": 0,
                    "escalated": False,
                    "source_meeting_id": meeting_id,
                }
            )
        return planned
