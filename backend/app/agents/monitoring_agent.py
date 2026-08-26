from datetime import datetime, timezone
from uuid import uuid4

from app.agents.action_agent import ActionAgent
from app.agents.decision_agent import DecisionAgent
from app.agents.task_manager_agent import TaskManagerAgent
from app.core.config import get_settings


class MonitoringAgent:
    def __init__(self) -> None:
        self.task_manager = TaskManagerAgent()
        self.decision_agent = DecisionAgent()
        self.action_agent = ActionAgent(self.task_manager)
        self.settings = get_settings()

    def _in_cooldown(self, task: dict, key: str, minutes: int) -> bool:
        last_ts = task.get(key)
        if not last_ts:
            return False
        if last_ts.tzinfo is None:
            last_ts = last_ts.replace(tzinfo=timezone.utc)
        elapsed = (datetime.now(timezone.utc) - last_ts).total_seconds()
        return elapsed < (minutes * 60)

    def _scheduled_interval_minutes(self, task: dict) -> int:
        deadline = task.get("deadline")
        if not deadline:
            return 24 * 60
        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)
        hours_left = (deadline - datetime.now(timezone.utc)).total_seconds() / 3600
        return 60 if hours_left <= 24 else 24 * 60

    async def run_cycle(self, inactivity_hours: int) -> dict:
        overdue_tasks = await self.task_manager.find_overdue()
        inactive_tasks = await self.task_manager.find_inactive(inactivity_hours)

        # Merge by task_id to avoid duplicate actions in the same cycle.
        task_map = {task["task_id"]: task for task in overdue_tasks + inactive_tasks}

        reminders = 0
        escalations = 0
        scanned = len(task_map)
        decisions = 0

        for task in task_map.values():
            if task.get("status") == "completed":
                continue

            decision = await self.decision_agent.decide(task)
            decisions += 1
            if decision["action"] != "none":
                await self.task_manager.insert_log(
                    {
                        "log_id": str(uuid4()),
                        "timestamp": datetime.now(timezone.utc),
                        "actor": "DecisionAgent",
                        "action": "ai_decision_made",
                        "reason": decision["reason"],
                        "task_id": task["task_id"],
                        "payload": {
                            "decision": decision["action"],
                            "overdue_demo_days": decision.get("overdue_demo_days", 0),
                            "owner": task.get("owner", "Unassigned"),
                        },
                    }
                )

            if decision["action"] == "remind":
                dynamic_minutes = self._scheduled_interval_minutes(task)
                allowed = await self.task_manager.acquire_reminder_slot(
                    task["task_id"], max(self.settings.reminder_cooldown_minutes, dynamic_minutes)
                )
                if not allowed:
                    await self.task_manager.insert_log(
                        {
                            "log_id": str(uuid4()),
                            "timestamp": datetime.now(timezone.utc),
                            "actor": "MonitoringAgent",
                            "action": "reminder_skipped_cooldown",
                            "reason": (
                                "Reminder blocked by cooldown policy "
                                f"(min {max(self.settings.reminder_cooldown_minutes, dynamic_minutes)} minutes)"
                            ),
                            "task_id": task["task_id"],
                            "payload": {"owner": task.get("owner", "Unassigned")},
                        }
                    )
                    continue
                reminders += 1
                await self.action_agent.remind(task, decision["reason"])
                await self.task_manager.tasks.update_one(
                    {"task_id": task["task_id"]},
                    {"$set": {"status": "delayed", "updated_at": datetime.now(timezone.utc)}},
                )
            elif decision["action"] == "escalate":
                dynamic_minutes = self._scheduled_interval_minutes(task)
                allowed = await self.task_manager.acquire_escalation_slot(
                    task["task_id"], max(self.settings.escalation_cooldown_minutes, dynamic_minutes)
                )
                if not allowed:
                    await self.task_manager.insert_log(
                        {
                            "log_id": str(uuid4()),
                            "timestamp": datetime.now(timezone.utc),
                            "actor": "MonitoringAgent",
                            "action": "escalation_skipped_cooldown",
                            "reason": (
                                "Escalation blocked by cooldown policy "
                                f"(min {max(self.settings.escalation_cooldown_minutes, dynamic_minutes)} minutes)"
                            ),
                            "task_id": task["task_id"],
                            "payload": {"owner": task.get("owner", "Unassigned")},
                        }
                    )
                    continue
                escalations += 1
                await self.action_agent.escalate(task, decision["reason"])
                await self.task_manager.tasks.update_one(
                    {"task_id": task["task_id"]},
                    {"$set": {"status": "delayed", "updated_at": datetime.now(timezone.utc)}},
                )
            else:
                scheduled_minutes = self._scheduled_interval_minutes(task)
                allowed = await self.task_manager.acquire_reminder_slot(task["task_id"], scheduled_minutes)
                if allowed:
                    reminders += 1
                    reason = (
                        "Scheduled follow-up reminder: daily cadence active"
                        if scheduled_minutes >= 24 * 60
                        else "Scheduled follow-up reminder: near-deadline hourly cadence active"
                    )
                    await self.action_agent.remind(task, reason)
                    await self.task_manager.insert_log(
                        {
                            "log_id": str(uuid4()),
                            "timestamp": datetime.now(timezone.utc),
                            "actor": "MonitoringAgent",
                            "action": "scheduled_reminder_sent",
                            "reason": reason,
                            "task_id": task["task_id"],
                            "payload": {
                                "interval_minutes": scheduled_minutes,
                                "owner": task.get("owner", "Unassigned"),
                            },
                        }
                    )

        return {
            "scanned": scanned,
            "decisions": decisions,
            "reminders": reminders,
            "escalations": escalations,
        }
