from fastapi import APIRouter, HTTPException

from app.models.schemas import MeetingInput
from app.services.orchestrator import WorkflowOrchestrator


router = APIRouter(prefix="/meetings", tags=["meetings"])


@router.post("/process")
async def process_meeting(meeting_input: MeetingInput) -> dict:
    try:
        orchestrator = WorkflowOrchestrator()
        return await orchestrator.process_meeting(meeting_input)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to process meeting: {exc}") from exc
