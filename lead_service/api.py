from typing import Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from .config import Settings
from .db import Database
from .service import LeadService
from .opportunity_agent import discover_opportunities as run_discovery


class LeadRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120, pattern=r".*\S.*")
    email: str = Field(
        min_length=5,
        max_length=320,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
    )
    need: str = Field(min_length=10, max_length=2000)
    phone: Optional[str] = Field(default=None, max_length=40)
    company: Optional[str] = Field(default=None, max_length=160)


class AppointmentRequest(BaseModel):
    requested_start: str = Field(min_length=10, max_length=80)


class OpportunityStatusRequest(BaseModel):
    status: str = Field(min_length=3, max_length=30)


def create_app(settings: Optional[Settings] = None) -> FastAPI:
    settings = settings or Settings.from_env()
    service = LeadService(
        Database(settings.database_path), settings.appointment_duration_minutes
    )
    app = FastAPI(title=f"{settings.business_name} Lead Booking API", version="0.1.0")
    app.state.lead_service = service
    demo_path = Path(__file__).with_name("static") / "index.html"

    @app.get("/", include_in_schema=False)
    def demo() -> FileResponse:
        return FileResponse(demo_path, media_type="text/html")

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok", "service": settings.business_name}

    @app.post("/leads", status_code=201)
    def create_lead(request: LeadRequest) -> dict:
        try:
            # dict() keeps the demo compatible with both Pydantic 1 and 2.
            return service.create_lead(**request.dict())
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.get("/leads/{lead_id}")
    def get_lead(lead_id: int) -> dict:
        try:
            return service.get_lead(lead_id)
        except LookupError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get("/leads")
    def list_leads() -> list[dict]:
        return service.list_leads()

    @app.post("/leads/{lead_id}/appointments", status_code=201)
    def book_appointment(lead_id: int, request: AppointmentRequest) -> dict:
        try:
            return service.book_appointment(lead_id, request.requested_start)
        except LookupError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @app.get("/appointments")
    def list_appointments() -> list[dict]:
        return service.list_appointments()

    @app.get("/metrics")
    def metrics() -> dict:
        """Local funnel metrics for demo and customer validation."""
        return service.funnel_summary()

    @app.post("/agent/discover", status_code=200)
    def discover_opportunities() -> dict:
        try:
            opportunities = run_discovery(service, settings.opportunity_feed_path)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return {"count": len(opportunities), "opportunities": opportunities}

    @app.get("/opportunities")
    def list_opportunities(status: Optional[str] = None) -> list[dict]:
        return service.list_opportunities(status)

    @app.patch("/opportunities/{opportunity_id}/status")
    def update_opportunity_status(
        opportunity_id: int, request: OpportunityStatusRequest
    ) -> dict:
        try:
            return service.update_opportunity_status(opportunity_id, request.status)
        except LookupError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    return app


app = create_app()
