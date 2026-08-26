import json
from datetime import datetime, timezone
from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage

from app.core.config import get_settings
from app.services.hf_fallback import HFFallbackService
from app.services.llm_client import LLMClient


class DecisionAgent:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.llm_client = LLMClient()
        self.hf_fallback = HFFallbackService()
        prompt_path = Path(__file__).resolve().parent.parent / "prompts" / "decision_prompt.txt"
        self.system_prompt = prompt_path.read_text(encoding="utf-8")

    async def decide(self, task: dict) -> dict:
        """Use simple deterministic policy, optionally enhanced with LLM explanation."""
        if task.get("escalated"):
            return {
                "action": "none",
                "reason": "Task is already escalated",
                "overdue_demo_days": 0,
            }

        now = datetime.now(timezone.utc)
        effective_deadline = task.get("simulated_deadline_at") or task.get("deadline")
        if effective_deadline.tzinfo is None:
            effective_deadline = effective_deadline.replace(tzinfo=timezone.utc)
        overdue_seconds = max(0.0, (now - effective_deadline).total_seconds())
        overdue_demo_days = overdue_seconds / max(1, self.settings.demo_day_seconds)

        action = "none"
        reason = "No action needed"
        if overdue_demo_days >= 2 or task.get("reminder_count", 0) >= 2:
            action = "escalate"
            reason = (
                f"AI detected delay: deadline exceeded by {overdue_demo_days:.1f} demo day(s); "
                "escalation triggered to reduce SLA breach risk"
            )
        elif overdue_demo_days > 0 or task.get("status") == "delayed":
            action = "remind"
            reason = (
                f"AI detected delay: deadline exceeded by {overdue_demo_days:.1f} demo day(s); "
                "sending proactive reminder"
            )

        llm = self.llm_client.get_chat_model()
        if llm is not None:
            llm_result = await self._llm_reasoning(task)
            if llm_result.get("action") in {"none", "remind", "escalate"}:
                action = llm_result["action"]
                reason = llm_result.get("reason", reason)
        elif self.settings.hf_fallback_enabled:
            payload = {
                "task": task.get("task"),
                "owner": task.get("owner"),
                "status": task.get("status"),
                "reminder_count": task.get("reminder_count", 0),
            }
            prompt = f"{self.system_prompt}\n\nInput:{json.dumps(payload)}\n\nJSON:"
            text = self.hf_fallback.run(prompt, max_new_tokens=160)
            try:
                parsed = json.loads(text.replace("```json", "").replace("```", "").strip())
                if parsed.get("action") in {"none", "remind", "escalate"}:
                    action = parsed["action"]
                    reason = parsed.get("reason", reason)
            except Exception:
                pass

        return {
            "action": action,
            "reason": reason,
            "overdue_demo_days": round(overdue_demo_days, 2),
        }

    async def _llm_reasoning(self, task: dict) -> dict:
        try:
            llm = self.llm_client.get_chat_model()
            if llm is None:
                return {}
            payload = {
                "task": task.get("task"),
                "owner": task.get("owner"),
                "status": task.get("status"),
                "deadline": task.get("deadline").isoformat(),
                "reminder_count": task.get("reminder_count", 0),
                "escalated": task.get("escalated", False),
            }
            response = await llm.ainvoke(
                [
                    SystemMessage(content=self.system_prompt),
                    HumanMessage(content=json.dumps(payload)),
                ]
            )
            return json.loads(response.content)
        except Exception:
            return {}
