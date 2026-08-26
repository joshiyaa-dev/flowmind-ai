from datetime import datetime, timezone
from uuid import uuid4

from app.agents.input_agent import InputAgent
from app.agents.planning_agent import PlanningAgent
from app.agents.task_manager_agent import TaskManagerAgent
from app.agents.understanding_agent import UnderstandingAgent
from app.models.schemas import MeetingInput
from app.services.notification_service import NotificationService


class WorkflowOrchestrator:
    def __init__(self) -> None:
        self.input_agent = InputAgent()
        self.understanding_agent = UnderstandingAgent()
        self.planning_agent = PlanningAgent()
        self.task_manager = TaskManagerAgent()
        self.notification_service = NotificationService()

    async def process_meeting(self, meeting_input: MeetingInput) -> dict:
        meeting_id = str(uuid4())
        clean_input = self.input_agent.sanitize(meeting_input)

        extracted = await self.understanding_agent.extract_tasks(clean_input)
        planned = self.planning_agent.plan(extracted, meeting_id)
        inserted = await self.task_manager.insert_tasks(planned)

        workers = self.notification_service.get_alert_recipients()
        for index, task in enumerate(inserted):
            assignee_email = workers[index % len(workers)] if workers else ""
            if assignee_email:
                await self.task_manager.assign_worker(task.get("task_id"), assignee_email)
                task["assignee_email"] = assignee_email

            msg = (
                "Task Created\n"
                f"Task: {task.get('task')}\n"
                f"Owner: {task.get('owner')}\n"
                f"Assigned Worker Email: {task.get('assignee_email', 'Not assigned')}\n"
                f"Deadline: {task.get('deadline')}\n"
                "Please start work on this task and share progress updates."
            )
            mail_result = self.notification_service.send_email_many(
                [assignee_email] if assignee_email else workers,
                "New Task Created - FlowMind AI",
                msg,
            )
            await self.task_manager.insert_log(
                {
                    "log_id": str(uuid4()),
                    "timestamp": datetime.now(timezone.utc),
                    "actor": "Orchestrator",
                    "action": "task_created_notified",
                    "reason": "Email notification sent for newly created task",
                    "task_id": task.get("task_id"),
                    "payload": {
                        "recipients": [assignee_email] if assignee_email else workers,
                        "assignee_email": assignee_email,
                        "email": mail_result,
                    },
                }
            )

        await self.task_manager.insert_log(
            {
                "log_id": str(uuid4()),
                "timestamp": datetime.now(timezone.utc),
                "actor": "Orchestrator",
                "action": "meeting_processed",
                "reason": "Meeting transcript analyzed and converted into tasks",
                "task_id": None,
                "payload": {
                    "meeting_id": meeting_id,
                    "source": meeting_input.source,
                    "input_preview": clean_input[:180],
                    "tasks_created": len(inserted),
                },
            }
        )

        return {
            "meeting_id": meeting_id,
            "tasks_created": len(inserted),
            "tasks": inserted,
        }
