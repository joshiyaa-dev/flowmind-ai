import asyncio

from fastapi import APIRouter

from app.agents.monitoring_agent import MonitoringAgent
from app.agents.task_manager_agent import TaskManagerAgent
from app.models.schemas import MeetingInput
from app.services.orchestrator import WorkflowOrchestrator


router = APIRouter(prefix="/demo", tags=["demo"])


@router.post("/run-script")
async def run_scripted_demo() -> dict:
    orchestrator = WorkflowOrchestrator()
    monitoring = MonitoringAgent()
    task_manager = TaskManagerAgent()

    scripted_input = MeetingInput(
        source="text",
        content=(
            "- Finalize enterprise onboarding checklist owner: sarvesh deadline: 2026-03-31\n"
            "- Send risk report to legal owner: sarvesh deadline: 2026-03-31\n"
            "- Validate payment gateway patch owner: sarvesh deadline: 2026-04-01"
        ),
    )

    created = await orchestrator.process_meeting(scripted_input)
    await asyncio.sleep(2)
    accelerated = await task_manager.force_demo_delay(limit=3)
    await asyncio.sleep(2)
    monitor_result = await monitoring.run_cycle(inactivity_hours=1)

    return {
        "ok": True,
        "tasks_created": created.get("tasks_created", 0),
        "tasks_accelerated": accelerated,
        "monitor_result": monitor_result,
        "message": "Full demo script executed",
    }


@router.post("/reset")
async def reset_demo_data() -> dict:
    task_manager = TaskManagerAgent()
    result = await task_manager.reset_demo_state()
    return {
        "ok": True,
        "message": "Demo data reset completed",
        **result,
    }
