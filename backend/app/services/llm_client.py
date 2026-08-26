from langchain_openai import ChatOpenAI

from app.core.config import get_settings


class LLMClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    def get_chat_model(self) -> ChatOpenAI | None:
        provider = self.settings.llm_provider.strip().lower()

        if provider == "groq" and self.settings.groq_api_key:
            return ChatOpenAI(
                model=self.settings.groq_model,
                api_key=self.settings.groq_api_key,
                base_url=self.settings.groq_base_url,
                temperature=0,
            )

        if provider == "openai" and self.settings.openai_api_key:
            return ChatOpenAI(
                model=self.settings.openai_model,
                api_key=self.settings.openai_api_key,
                base_url=self.settings.openai_base_url,
                temperature=0,
            )

        # Fallback to whichever key is available.
        if self.settings.groq_api_key:
            return ChatOpenAI(
                model=self.settings.groq_model,
                api_key=self.settings.groq_api_key,
                base_url=self.settings.groq_base_url,
                temperature=0,
            )
        if self.settings.openai_api_key:
            return ChatOpenAI(
                model=self.settings.openai_model,
                api_key=self.settings.openai_api_key,
                base_url=self.settings.openai_base_url,
                temperature=0,
            )
        return None
