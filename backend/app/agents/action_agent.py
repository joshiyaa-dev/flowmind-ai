from datetime import datetime, timezone
from uuid import uuid4

from app.agents.task_manager_agent import TaskManagerAgent
from app.services.notification_service import NotificationService


class ActionAgent:
    def __init__(self, task_manager: TaskManagerAgent) -> None:
        self.task_manager = task_manager
        self.notification_service = NotificationService()

    def _message(self, task: dict, action: str, reason: str) -> str:
        return (
            f"Workflow Alert\n"
            f"Task: {task.get('task')}\n"
            f"Owner: {task.get('owner')}\n"
            f"Assigned Worker Email: {task.get('assignee_email', 'Not assigned')}\n"
            f"Action: {action}\n"
            f"Reason: {reason}\n"
            f"Please work on this task and share updates as needed.\n"
            f"Business Deadline: {task.get('deadline')}"
        )

    def _recipients_for_task(self, task: dict) -> list[str]:
        assignee = str(task.get("assignee_email") or "").strip()
        if assignee:
            return [assignee]
        return self.notification_service.get_alert_recipients()

    async def remind(self, task: dict, reason: str) -> None:
        recipients = self._recipients_for_task(task)
        message = self._message(task, "remind", reason)
        email_result = self.notification_service.send_email_many(recipients, "Task Reminder - FlowMind AI", message)

        await self.task_manager.increment_reminder(task["task_id"])
        await self.task_manager.insert_log(
            {
                "log_id": str(uuid4()),
                "timestamp": datetime.now(timezone.utc),
                "actor": "ActionAgent",
                "action": "reminder_sent",
                "reason": reason,
                "task_id": task["task_id"],
                "payload": {
                    "channel": "smtp",
                    "recipients": recipients,
                    "owner": task["owner"],
                    "task": task["task"],
                    "email": email_result,
                },
            }
        )

    async def escalate(self, task: dict, reason: str) -> None:
        recipients = self._recipients_for_task(task)
        message = self._message(task, "escalate", reason)
        email_result = self.notification_service.send_email_many(recipients, "Escalation - FlowMind AI", message)

        await self.task_manager.mark_escalated(task["task_id"])
        await self.task_manager.insert_log(
            {
                "log_id": str(uuid4()),
                "timestamp": datetime.now(timezone.utc),
                "actor": "ActionAgent",
                "action": "escalation_triggered",
                "reason": reason,
                "task_id": task["task_id"],
                "payload": {
                    "channel": "smtp",
                    "manager": "Ops Lead",
                    "recipients": recipients,
                    "owner": task["owner"],
                    "task": task["task"],
                    "email": email_result,
                },
            }
        )
