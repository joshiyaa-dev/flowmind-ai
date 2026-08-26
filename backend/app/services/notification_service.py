import json
import smtplib
import time
from email.mime.text import MIMEText

from app.core.config import get_settings


class NotificationService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def get_alert_recipients(self) -> list[str]:
        values = [item.strip() for item in self.settings.alert_recipients_csv.split(",") if item.strip()]
        deduped: list[str] = []
        for email in values:
            if email not in deduped:
                deduped.append(email)
        return deduped

    def resolve_contact(self, owner: str) -> dict:
        try:
            directory = json.loads(self.settings.contact_directory_json or "{}")
            owner_data = directory.get(owner, {})
        except Exception:
            owner_data = {}

        safe_name = "".join(ch for ch in owner.lower() if ch.isalnum()) or "team"
        return {
            "email": owner_data.get("email") or f"{safe_name}@example.com",
            "manager_email": owner_data.get("manager_email") or self.settings.manager_email,
        }

    def send_email(self, to_email: str, subject: str, body: str) -> dict:
        if not self.settings.email_user or not self.settings.email_pass:
            return {"ok": False, "channel": "email", "error": "EMAIL_USER/EMAIL_PASS not set"}

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = self.settings.email_user
        msg["To"] = to_email

        last_error = ""
        for attempt in range(3):
            try:
                with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port, timeout=15) as server:
                    server.starttls()
                    server.login(self.settings.email_user, self.settings.email_pass)
                    server.send_message(msg)
                return {"ok": True, "channel": "email", "recipient": to_email}
            except Exception as exc:
                last_error = str(exc)
                time.sleep(0.4 * (attempt + 1))

        return {"ok": False, "channel": "email", "error": last_error}

    def send_email_many(self, to_emails: list[str], subject: str, body: str) -> dict:
        results = [self.send_email(to_email, subject, body) for to_email in to_emails]
        sent = len([r for r in results if r.get("ok")])
        failed = len(results) - sent
        return {
            "ok": failed == 0 and len(results) > 0,
            "channel": "email",
            "sent": sent,
            "failed": failed,
            "results": results,
        }
