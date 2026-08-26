from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


TaskStatus = Literal["pending", "completed", "delayed"]


class MeetingInput(BaseModel):
    source: Literal["text", "voice"] = "text"
    content: str = Field(min_length=5, max_length=12000)


class ExtractedTask(BaseModel):
    task: str
    owner: str
    deadline: str


class TaskRecord(BaseModel):
    task_id: str
    task: str
    owner: str
    deadline: datetime
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    last_activity_at: datetime
    reminder_count: int
    escalated: bool
    source_meeting_id: str


class UpdateTaskStatusRequest(BaseModel):
    status: TaskStatus


class UpdateTaskRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    owner: str | None = None
    deadline: datetime | None = None


class AuditLogRecord(BaseModel):
    log_id: str
    timestamp: datetime
    actor: str
    action: str
    reason: str
    task_id: str | None = None
    payload: dict = Field(default_factory=dict)
