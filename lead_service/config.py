from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    database_path: str = "leads.db"
    business_name: str = "Local Demo Business"
    appointment_duration_minutes: int = 30

    @classmethod
    def from_env(cls) -> "Settings":
        duration = int(os.getenv("APPOINTMENT_DURATION_MINUTES", "30"))
        if duration <= 0 or duration > 480:
            raise ValueError("APPOINTMENT_DURATION_MINUTES must be between 1 and 480")
        database_path = os.getenv("LEAD_DATABASE_PATH", "leads.db")
        if database_path != ":memory:":
            Path(database_path).expanduser().parent.mkdir(parents=True, exist_ok=True)
        return cls(
            database_path=database_path,
            business_name=os.getenv("BUSINESS_NAME", "Local Demo Business"),
            appointment_duration_minutes=duration,
        )
