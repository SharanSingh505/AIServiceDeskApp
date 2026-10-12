"""Local API for the AI-Powered Service Desk MVP."""

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from assignment_engine import recommend
from database import (assign_ticket as save_assignment, create_ticket as save_ticket,
                      get_engineer, get_ticket, initialize_database,  list_engineers as database_list_engineers,
                      list_tickets as database_list_tickets)

app = FastAPI(title="AI Service Desk MVP", version="0.1.0")


class TicketCreate(BaseModel):
    summary: str = Field(min_length=5, max_length=200)
    category: str = Field(description="Example: vpn, iam, m365")
    priority: str = Field(pattern="^P[1-4]$")
    business_impact: str = Field(min_length=3, max_length=200)


def find_ticket(ticket_id: str) -> dict:
    ticket = get_ticket(ticket_id)
    if ticket:
        return ticket
    raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} was not found")


def find_engineer(engineer_id: str) -> dict:
    engineer = get_engineer(engineer_id)
    if engineer:
        return engineer
    raise HTTPException(status_code=404, detail=f"Engineer {engineer_id} was not found")


@app.on_event("startup")
def startup() -> None:
    initialize_database()


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "mode": "local sample data"}


@app.get("/api/tickets")
def list_tickets() -> list[dict]:
    return database_list_tickets()


@app.get("/api/engineers")
def list_engineers() -> list[dict]:
    return  database_list_engineers()


@app.get("/api/dashboard")
def get_dashboard() -> dict:
    tickets = database_list_tickets()
    engineers = list_engineers()
    open_tickets = [ticket for ticket in tickets if ticket.get("status", "New") != "Assigned"]
    at_risk = []
    for ticket in open_tickets:
        recommendation = recommend(ticket, engineers)["recommendation"]
        if not recommendation["likely_to_meet_sla"]:
            at_risk.append({"ticket_id": ticket["id"], "summary": ticket["summary"], "priority": ticket["priority"]})
    return {
        "open_ticket_count": len(open_tickets),
        "assigned_ticket_count": len(tickets) - len(open_tickets),
        "at_risk_count": len(at_risk),
        "at_risk_tickets": at_risk,
        "engineers": engineers,
    }


@app.get("/api/tickets/{ticket_id}/recommendation")
def get_recommendation(ticket_id: str) -> dict:
    return recommend(find_ticket(ticket_id), list_engineers())


@app.post("/api/tickets/{ticket_id}/assign")
def assign_ticket(ticket_id: str, engineer_id: str) -> dict:
    """Manager-approved assignment; this models the later ServiceNow update."""
    find_ticket(ticket_id)
    engineer = find_engineer(engineer_id)
    ticket = save_assignment(ticket_id, engineer)
    return {"ticket": ticket, "message": f"{ticket_id} assigned to {engineer['name']}"}


@app.post("/api/tickets", status_code=201)
def create_ticket(payload: TicketCreate) -> dict:
    ticket = save_ticket({"created_at": "local-demo", **payload.model_dump()})
    result = recommend(ticket, list_engineers())
    return {"ticket": ticket, **result}


app.mount("/", StaticFiles(directory=Path(__file__).parent / "web", html=True), name="web")
