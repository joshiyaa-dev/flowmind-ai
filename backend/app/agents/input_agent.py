from app.models.schemas import MeetingInput


class InputAgent:
    @staticmethod
    def sanitize(meeting: MeetingInput) -> str:
        """Normalize incoming text/voice transcript into a clean string."""
        text = meeting.content.strip().replace("\r\n", "\n")
        return "\n".join(line.strip() for line in text.split("\n") if line.strip())
