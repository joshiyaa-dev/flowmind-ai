from functools import lru_cache

from app.core.config import get_settings


@lru_cache(maxsize=1)
def _get_pipeline():
    from transformers import pipeline  # Imported lazily so app still runs without transformers.

    settings = get_settings()
    return pipeline(
        "text-generation",
        model=settings.hf_model_id,
        device_map="auto",
    )


class HFFallbackService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def run(self, prompt: str, max_new_tokens: int = 280) -> str:
        if not self.settings.hf_fallback_enabled:
            return ""

        try:
            model_pipeline = _get_pipeline()
            output = model_pipeline(prompt, max_new_tokens=max_new_tokens, do_sample=False)
            if not output:
                return ""
            return str(output[0].get("generated_text", ""))
        except Exception:
            return ""
