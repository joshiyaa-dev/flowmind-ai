import json
import re
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from app.core.config import get_settings
from app.services.hf_fallback import HFFallbackService
from app.services.llm_client import LLMClient


class UnderstandingAgent:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.llm_client = LLMClient()
        self.hf_fallback = HFFallbackService()
        prompt_path = Path(__file__).resolve().parent.parent / "prompts" / "understanding_prompt.txt"
        self.system_prompt = prompt_path.read_text(encoding="utf-8")

    async def extract_tasks(self, meeting_text: str) -> list[dict[str, Any]]:
        """Extract tasks with retries, then fallback parser if LLM output is unusable."""
        llm = self.llm_client.get_chat_model()
        if llm is not None:
            for _ in range(2):
                result = await self._run_llm_parse(meeting_text, llm)
                if result:
                    return result
            # Retry with a stricter follow-up prompt.
            fallback_prompt = (
                meeting_text
                + "\n\nReturn valid JSON array only. No prose."
            )
            result = await self._run_llm_parse(fallback_prompt, llm)
            if result:
                return result

        if self.settings.hf_fallback_enabled:
            prompt = f"{self.system_prompt}\n\nTranscript:\n{meeting_text}\n\nJSON:"
            hf_raw = self.hf_fallback.run(prompt)
            result = self._safe_json_parse(hf_raw)
            if result:
                return result

        return self._heuristic_fallback(meeting_text)

    async def _run_llm_parse(self, meeting_text: str, llm) -> list[dict[str, Any]]:
        try:
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=meeting_text),
            ]
            response = await llm.ainvoke(messages)
            return self._safe_json_parse(str(response.content))
        except Exception:
            return []

    def _safe_json_parse(self, raw: str) -> list[dict[str, Any]]:
        cleaned = raw.strip()
        if "```" in cleaned:
            cleaned = cleaned.replace("```json", "").replace("```", "").strip()
        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, list):
                return [self._normalize_item(item) for item in parsed if isinstance(item, dict)]
        except Exception:
            pass
        return []

    def _normalize_item(self, item: dict[str, Any]) -> dict[str, str]:
        raw_deadline = str(item.get("deadline", "")).strip()
        deadline = self._safe_deadline(raw_deadline)
        return {
            "task": str(item.get("task", "")).strip()[:120] or "Follow up on discussed action",
            "owner": str(item.get("owner", "Unassigned")).strip() or "Unassigned",
            "deadline": deadline,
        }

    def _safe_deadline(self, raw_deadline: str) -> str:
        if not raw_deadline:
            return str(date.today() + timedelta(days=7))
        try:
            parsed = datetime.fromisoformat(raw_deadline)
            return parsed.date().isoformat()
        except Exception:
            return str(date.today() + timedelta(days=7))

    def _heuristic_fallback(self, meeting_text: str) -> list[dict[str, str]]:
        tasks: list[dict[str, str]] = []
        lines = [ln.strip("-• ").strip() for ln in meeting_text.splitlines() if ln.strip()]
        owner_pattern = re.compile(r"owner\s*:\s*([^,;]+?)(?=\s+deadline\s*:|$)", re.IGNORECASE)
        deadline_pattern = re.compile(r"deadline\s*:\s*(\d{4}-\d{2}-\d{2})", re.IGNORECASE)

        for line in lines:
            if len(line) < 8:
                continue
            owner_match = owner_pattern.search(line)
            date_match = deadline_pattern.search(line)
            task_text = re.sub(r"owner\s*:\s*[^,;]+(?=\s+deadline\s*:|$)", "", line, flags=re.IGNORECASE)
            task_text = re.sub(r"deadline\s*:\s*\d{4}-\d{2}-\d{2}", "", task_text, flags=re.IGNORECASE)
            task_text = re.sub(r"\s+", " ", task_text).strip(" -:")
            tasks.append(
                {
                    "task": (task_text or line)[:120],
                    "owner": owner_match.group(1).strip() if owner_match else "Unassigned",
                    "deadline": date_match.group(1) if date_match else str(date.today() + timedelta(days=7)),
                }
            )

        if not tasks:
            tasks.append(
                {
                    "task": "Review meeting notes and define concrete owner and deadline",
                    "owner": "Unassigned",
                    "deadline": str(date.today() + timedelta(days=7)),
                }
            )
        return tasks
