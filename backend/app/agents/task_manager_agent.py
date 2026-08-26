from datetime import datetime, timedelta, timezone
from typing import Any

from app.core.database import get_db
from pymongo import ReturnDocument


class TaskManagerAgent:
    def __init__(self) -> None:
        self.db = get_db()
        self.tasks = self.db["tasks"]
        self.logs = self.db["audit_logs"]

    async def insert_tasks(self, tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not tasks:
            return []

        prepared: list[dict[str, Any]] = []
        for item in tasks:
            normalized = dict(item)
            normalized["deadline"] = self._to_utc_datetime(item["deadline"])
            if item.get("simulated_deadline_at"):
                normalized["simulated_deadline_at"] = self._to_utc_datetime(item["simulated_deadline_at"])
            prepared.append(normalized)

        await self.tasks.insert_many(prepared)
        for item in prepared:
            item.pop("_id", None)
        return prepared

    async def list_tasks(self) -> list[dict[str, Any]]:
        cursor = self.tasks.find({}, {"_id": 0}).sort("created_at", -1)
        return await cursor.to_list(length=500)

    async def update_status(self, task_id: str, status: str) -> bool:
        now = datetime.now(timezone.utc)
        result = await self.tasks.update_one(
            {"task_id": task_id},
            {"$set": {"status": status, "updated_at": now, "last_activity_at": now}},
        )
        return result.modified_count > 0

    async def assign_worker(self, task_id: str, assignee_email: str) -> bool:
        now = datetime.now(timezone.utc)
        result = await self.tasks.update_one(
            {"task_id": task_id},
            {
                "$set": {
                    "assignee_email": assignee_email,
                    "updated_at": now,
                }
            },
        )
        return result.modified_count > 0

    async def update_task(self, task_id: str, fields: dict[str, Any]) -> bool:
        """Edit editable task fields (title/description/owner/deadline)."""
        if not fields:
            return False
        now = datetime.now(timezone.utc)
        updates: dict[str, Any] = {"updated_at": now, "last_activity_at": now}
        if "title" in fields and fields["title"] is not None:
            updates["title"] = fields["title"]
        if "description" in fields and fields["description"] is not None:
            updates["description"] = fields["description"]
        if "owner" in fields and fields["owner"] is not None:
            updates["assignee_email"] = fields["owner"]
        if "deadline" in fields and fields["deadline"] is not None:
            deadline = fields["deadline"]
            if isinstance(deadline, str):
                deadline = datetime.fromisoformat(deadline.replace("Z", "+00:00"))
            updates["deadline"] = self._to_utc_datetime(deadline)
            # Keep the simulated clock in sync with a real edit.
            updates["simulated_deadline_at"] = updates["deadline"]
        result = await self.tasks.update_one({"task_id": task_id}, {"$set": updates})
        return result.modified_count > 0

    async def delete_task(self, task_id: str) -> bool:
        result = await self.tasks.delete_one({"task_id": task_id})
        return result.deleted_count > 0

    async def find_overdue(self) -> list[dict[str, Any]]:
        now = datetime.now(timezone.utc)
        cursor = self.tasks.find(
            {
                "status": {"$ne": "completed"},
                "$or": [
                    {"simulated_deadline_at": {"$lt": now}},
                    {
                        "simulated_deadline_at": {"$exists": False},
                        "deadline": {"$lt": now},
                    },
                ],
            },
            {"_id": 0},
        )
        return await cursor.to_list(length=500)

    async def find_inactive(self, inactivity_hours: int) -> list[dict[str, Any]]:
        threshold = datetime.now(timezone.utc)
        threshold = threshold.replace(microsecond=0)
        threshold = threshold.timestamp() - (inactivity_hours * 3600)
        threshold_dt = datetime.fromtimestamp(threshold, tz=timezone.utc)
        cursor = self.tasks.find(
            {
                "status": {"$ne": "completed"},
                "last_activity_at": {"$lt": threshold_dt},
            },
            {"_id": 0},
        )
        return await cursor.to_list(length=500)

    async def increment_reminder(self, task_id: str) -> None:
        now = datetime.now(timezone.utc)
        await self.tasks.update_one(
            {"task_id": task_id},
            {
                "$inc": {"reminder_count": 1},
                "$set": {
                    "updated_at": now,
                    "last_reminder_at": now,
                    "last_activity_at": now,
                },
            },
        )

    async def mark_escalated(self, task_id: str) -> None:
        now = datetime.now(timezone.utc)
        await self.tasks.update_one(
            {"task_id": task_id},
            {
                "$set": {
                    "escalated": True,
                    "updated_at": now,
                    "last_escalation_at": now,
                    "last_activity_at": now,
                }
            },
        )

    async def acquire_reminder_slot(self, task_id: str, cooldown_minutes: int) -> bool:
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(minutes=cooldown_minutes)
        result = await self.tasks.find_one_and_update(
            {
                "task_id": task_id,
                "$or": [
                    {"last_reminder_at": {"$exists": False}},
                    {"last_reminder_at": {"$lt": cutoff}},
                ],
            },
            {
                "$set": {
                    "last_reminder_at": now,
                    "updated_at": now,
                }
            },
            return_document=ReturnDocument.AFTER,
        )
        return result is not None

    async def acquire_escalation_slot(self, task_id: str, cooldown_minutes: int) -> bool:
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(minutes=cooldown_minutes)
        result = await self.tasks.find_one_and_update(
            {
                "task_id": task_id,
                "$or": [
                    {"last_escalation_at": {"$exists": False}},
                    {"last_escalation_at": {"$lt": cutoff}},
                ],
            },
            {
                "$set": {
                    "last_escalation_at": now,
                    "updated_at": now,
                }
            },
            return_document=ReturnDocument.AFTER,
        )
        return result is not None

    async def insert_log(self, log_doc: dict[str, Any]) -> None:
        await self.logs.insert_one(log_doc)

    async def list_logs(self) -> list[dict[str, Any]]:
        cursor = self.logs.find({}, {"_id": 0}).sort("timestamp", -1)
        return await cursor.to_list(length=800)

    async def reset_demo_state(self) -> dict[str, int]:
        task_result = await self.tasks.delete_many({})
        log_result = await self.logs.delete_many({})
        return {
            "tasks_deleted": int(task_result.deleted_count),
            "logs_deleted": int(log_result.deleted_count),
        }

    async def force_demo_delay(self, limit: int = 2) -> int:
        now = datetime.now(timezone.utc)
        pending = await self.tasks.find(
            {"status": "pending"},
            {"_id": 0, "task_id": 1},
        ).limit(limit).to_list(length=limit)
        if not pending:
            return 0

        task_ids = [row["task_id"] for row in pending]
        result = await self.tasks.update_many(
            {"task_id": {"$in": task_ids}},
            {
                "$set": {
                    "simulated_deadline_at": now,
                    "updated_at": now,
                }
            },
        )
        return result.modified_count

    @staticmethod
    def _to_utc_datetime(value: Any) -> datetime:
        if isinstance(value, datetime):
            dt = value
        else:
            dt = datetime.fromisoformat(str(value))
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
