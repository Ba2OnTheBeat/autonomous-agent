# Lead booking MVP

This repository now includes a small, local-first revenue-operations demo. Its opportunity agent discovers and scores mock job-board opportunities, queues them for human review, and separately accepts inbound leads, qualifies them, and books appointments against a SQLite-backed mock calendar. It does not send email, text messages, proposals, or other unsolicited outreach.

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
| `OPPORTUNITY_FEED_PATH` | unset | Optional local JSON export used by the opportunity agent |

## Run

```powershell
python run_service.py
```

Open `http://127.0.0.1:8000/` for the guided browser demo, or `http://127.0.0.1:8000/docs` for interactive Swagger API documentation. The demo submits a lead, shows its qualification result, and reveals appointment booking only for qualified leads. Use `POST /agent/discover` in Swagger to run the local opportunity agent, then inspect ranked results at `GET /opportunities`. It uses mock opportunities and sends nothing externally.

To test with your own approved export, set `OPPORTUNITY_FEED_PATH` to a JSON array file containing `external_id`, `title`, `source`, `url`, `summary`, and optional `budget` fields. The agent reads that local file, scores the opportunities, and queues them for review; it does not contact the source.

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

The API also exposes `GET /health`, `GET /leads`, `GET /leads/{id}`, `GET /appointments`, `GET /metrics`, `POST /agent/discover`, and `GET /opportunities` for a simple operator/demo view. Discovered opportunities are scored and persisted with `new`, `reviewed`, `proposal_ready`, or `archived` statuses. Input lengths, email shape, timezone-aware ISO-8601 appointment times, and business rules are validated before persistence.

This is an honest foundation for an automated revenue workflow, not a promise of automatic profit: the current version finds and prioritizes opportunities locally, while proposal sending, payments, CRM sync, and external job-board/calendar integrations remain deliberate future integrations requiring customer consent and credentials. The safe next step is to add one approved connector and an explicit human approval gate before any external action.

## Test

```powershell
python -m unittest discover -s tests -v
```
