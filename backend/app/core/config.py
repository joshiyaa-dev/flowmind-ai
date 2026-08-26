from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FlowMind AI Agent"
    api_prefix: str = "/api"
    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db: str = "agentic_workflows"
    llm_provider: str = "groq"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_base_url: str = "https://api.openai.com/v1"
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    groq_base_url: str = "https://api.groq.com/openai/v1"
    hf_fallback_enabled: bool = False
    hf_model_id: str = "microsoft/Phi-3-mini-4k-instruct"
    monitor_interval_seconds: int = 10
    inactivity_hours: int = 24
    demo_day_seconds: int = 10
    reminder_cooldown_minutes: int = 60
    escalation_cooldown_minutes: int = 60
    email_user: str = ""
    email_pass: str = ""
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    manager_email: str = "manager@example.com"
    manager_phone: str = "+10000000000"
    contact_directory_json: str = "{}"
    alert_recipients_csv: str = "krishnaahari05@gmail.com,sarvesh7120@gmail.com"
    admin_token: str = ""  # when set, destructive/admin routes require X-Admin-Token header

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
