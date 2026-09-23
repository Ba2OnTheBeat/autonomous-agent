# Lead booking MVP

This repository now includes a small, local-first lead-generation demo. It accepts an inbound lead, performs lightweight qualification, and books a requested appointment against a SQLite-backed mock calendar. It does not send email, text messages, or other unsolicited outreach.

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Optional environment variables:

| Variable | Default | Purpose |
| --- | --- | --- |
| `LEAD_DATABASE_PATH` | `leads.db` | SQLite database path (`:memory:` is useful for tests) |
| `BUSINESS_NAME` | `Local Demo Business` | Name returned by the health endpoint |
| `APPOINTMENT_DURATION_MINUTES` | `30` | Length of each local mock-calendar booking |

## Run

```powershell
python run_service.py
```

Open `http://127.0.0.1:8000/` for the guided browser demo, or `http://127.0.0.1:8000/docs` for interactive Swagger API documentation. The demo submits a lead, shows its qualification result, and reveals appointment booking only for qualified leads. It uses a local SQLite mock calendar and sends nothing externally.

Example API requests:

```powershell
curl.exe -X POST http://127.0.0.1:8000/leads `
  -H "Content-Type: application/json" `
  -d '{\"name\":\"Ada Lovelace\",\"email\":\"ada@example.com\",\"need\":\"We need help booking qualified sales appointments.\"}'

curl.exe -X POST http://127.0.0.1:8000/leads/1/appointments `
  -H "Content-Type: application/json" `
  -d '{\"requested_start\":\"2027-01-10T15:00:00+00:00\"}'
```

Leads with a need of at least 20 characters are qualified; shorter valid needs are retained as `needs_review` and cannot book until a future review process qualifies them. Appointments reject past, malformed, and overlapping times.

The API also exposes `GET /health`, `GET /leads`, `GET /leads/{id}`, `GET /appointments`, and `GET /metrics` for a simple operator/demo view. `/metrics` reports the local funnel counts (`leads`, `qualified_leads`, and `booked_appointments`) so a customer pilot can measure whether the workflow creates value. Input lengths, email shape, timezone-aware ISO-8601 appointment times, and business rules are validated before persistence.

This is an honest foundation for an automated revenue workflow, not a promise of automatic profit: the current version handles inbound demand and booking locally, while outreach, payments, CRM sync, and calendar integrations remain deliberate future integrations requiring customer consent and credentials.

## Test

```powershell
python -m unittest discover -s tests -v
```
