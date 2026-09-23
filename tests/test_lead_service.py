import unittest
from datetime import datetime, timedelta, timezone

from lead_service.db import Database
from lead_service.service import LeadService


class LeadServiceTests(unittest.TestCase):
    def setUp(self):
        self.service = LeadService(Database(":memory:"))

    def test_lead_is_persisted_and_qualified(self):
        lead = self.service.create_lead(
            "Ada Lovelace", "ADA@example.com", "We need a recurring appointment booking workflow."
        )
        self.assertEqual(lead["email"], "ada@example.com")
        self.assertEqual(lead["qualification_status"], "qualified")
        self.assertEqual(self.service.get_lead(lead["id"])["name"], "Ada Lovelace")

    def test_unqualified_lead_cannot_book(self):
        lead = self.service.create_lead("Al", "al@example.com", "Need help today")
        with self.assertRaisesRegex(ValueError, "must be qualified"):
            self.service.book_appointment(lead["id"], self.future_time())

    def test_booking_rejects_overlapping_slot(self):
        lead = self.service.create_lead(
            "Ada Lovelace", "ada@example.com", "We need a recurring appointment booking workflow."
        )
        start = self.future_time()
        self.service.book_appointment(lead["id"], start)
        with self.assertRaisesRegex(ValueError, "unavailable"):
            self.service.book_appointment(lead["id"], start)

    def test_invalid_email_and_short_need_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "email"):
            self.service.create_lead("Ada Lovelace", "not-an-email", "A valid enough need")
        with self.assertRaisesRegex(ValueError, "need"):
            self.service.create_lead("Ada Lovelace", "ada@example.com", "short")

    def test_past_and_timezone_less_appointments_are_rejected(self):
        lead = self.service.create_lead(
            "Ada Lovelace", "ada@example.com", "We need a recurring appointment booking workflow."
        )
        with self.assertRaisesRegex(ValueError, "future"):
            self.service.book_appointment(lead["id"], "2020-01-01T10:00:00+00:00")
        with self.assertRaisesRegex(ValueError, "timezone"):
            self.service.book_appointment(lead["id"], "2030-01-01T10:00:00")

    def test_funnel_summary_and_appointment_list_include_context(self):
        lead = self.service.create_lead(
            "Ada Lovelace", "ada@example.com", "We need a recurring appointment booking workflow."
        )
        self.service.book_appointment(lead["id"], self.future_time())
        self.assertEqual(
            self.service.funnel_summary(),
            {"leads": 1, "qualified_leads": 1, "booked_appointments": 1},
        )
        appointment = self.service.list_appointments()[0]
        self.assertEqual(appointment["lead_name"], "Ada Lovelace")
        self.assertEqual(appointment["lead_email"], "ada@example.com")

    @staticmethod
    def future_time():
        return (datetime.now(timezone.utc) + timedelta(days=1)).replace(
            minute=0, second=0, microsecond=0
        ).isoformat()


if __name__ == "__main__":
    unittest.main()
