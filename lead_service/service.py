from datetime import datetime, timedelta, timezone
import re
from typing import Any, Dict, Optional

from .db import Database


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_datetime(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("requested_start must be a valid ISO-8601 datetime") from exc
    if parsed.tzinfo is None:
        raise ValueError("requested_start must include a timezone")
    return parsed.astimezone(timezone.utc)


class LeadService:
    def __init__(self, database: Database, appointment_duration_minutes: int = 30):
        self.database = database
        self.appointment_duration_minutes = appointment_duration_minutes

    def create_lead(
        self, name: str, email: str, need: str, phone: Optional[str] = None,
        company: Optional[str] = None,
    ) -> Dict[str, Any]:
        name, email, need = name.strip(), email.strip().lower(), need.strip()
        if len(name) < 2:
            raise ValueError("name must contain at least 2 characters")
        if not EMAIL_RE.match(email):
            raise ValueError("email must be valid")
        if len(need) < 10:
            raise ValueError("need must contain at least 10 characters")
        qualification = "qualified" if len(need) >= 20 else "needs_review"
        created_at = utc_now().isoformat()
        with self.database.connection() as connection:
            cursor = connection.execute(
                """INSERT INTO leads
                (name, email, phone, company, need, qualification_status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (name, email, phone, company, need, qualification, created_at),
            )
            lead_id = cursor.lastrowid
        return self.get_lead(lead_id)

    def get_lead(self, lead_id: int) -> Dict[str, Any]:
        with self.database.connection() as connection:
            row = connection.execute("SELECT * FROM leads WHERE id = ?", (lead_id,)).fetchone()
        if row is None:
            raise LookupError("lead not found")
        return dict(row)

    def book_appointment(self, lead_id: int, requested_start: str) -> Dict[str, Any]:
        lead = self.get_lead(lead_id)
        if lead["qualification_status"] != "qualified":
            raise ValueError("lead must be qualified before booking")
        start = parse_datetime(requested_start)
        if start <= utc_now():
            raise ValueError("requested_start must be in the future")
        end = start + timedelta(minutes=self.appointment_duration_minutes)
        with self.database.connection() as connection:
            conflict = connection.execute(
                """SELECT 1 FROM appointments
                   WHERE status = 'booked' AND starts_at < ? AND ends_at > ?""",
                (end.isoformat(), start.isoformat()),
            ).fetchone()
            if conflict:
                raise ValueError("requested time is unavailable")
            cursor = connection.execute(
                """INSERT INTO appointments
                (lead_id, starts_at, ends_at, status, created_at)
                VALUES (?, ?, ?, 'booked', ?)""",
                (lead_id, start.isoformat(), end.isoformat(), utc_now().isoformat()),
            )
            appointment_id = cursor.lastrowid
            row = connection.execute(
                "SELECT * FROM appointments WHERE id = ?", (appointment_id,)
            ).fetchone()
        return dict(row)

    def list_appointments(self) -> list[Dict[str, Any]]:
        with self.database.connection() as connection:
            rows = connection.execute(
                "SELECT * FROM appointments ORDER BY starts_at"
            ).fetchall()
        return [dict(row) for row in rows]
