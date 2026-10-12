import json
import logging

import azure.functions as func

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

ENGINEERS = [
    {"id": "eng-001", "name": "Jordan Lee", "team": "Network Support",
     "skills": ["vpn", "network", "azure"], "open_effort_hours": 2.0},
    {"id": "eng-002", "name": "Priya Patel", "team": "Identity & Access",
     "skills": ["iam", "mfa", "azure", "access"], "open_effort_hours": 3.5},
    {"id": "eng-003", "name": "Morgan Chen", "team": "Workplace Support",
     "skills": ["email", "device", "m365", "teams"], "open_effort_hours": 1.0},
]

SLA_HOURS = {"P1": 4.0, "P2": 8.0, "P3": 24.0, "P4": 72.0}
BASE_HOURS = {"P1": 4.0, "P2": 2.5, "P3": 1.5, "P4": 1.0}
ALIASES = {
    "identity & access": "iam",
    "identity and access": "iam",
    "microsoft 365": "m365",
}


def calculate_recommendation(ticket: dict) -> dict:
    category = ALIASES.get(ticket["category"].strip().lower(),
                           ticket["category"].strip().lower())
    priority = ticket["priority"].upper()[:2]

    if priority not in SLA_HOURS:
        raise ValueError("priority must be P1, P2, P3, or P4")

    results = []

    for engineer in ENGINEERS:
        workload = engineer["open_effort_hours"]
        skill_score = 40 if category in engineer["skills"] else 0
        workload_score = max(0, round(25 * (1 - workload / 8), 1))
        predicted_hours = round(BASE_HOURS[priority] + workload * 0.35, 1)
        sla_target = SLA_HOURS[priority]
        sla_score = 20 if predicted_hours <= sla_target else 0

        results.append({
            "engineer_id": engineer["id"],
            "engineer_name": engineer["name"],
            "team": engineer["team"],
            "total_score": round(skill_score + 15 + workload_score + sla_score, 1),
            "predicted_resolution_hours": predicted_hours,
            "sla_target_hours": sla_target,
            "sla_risk": "Likely to Meet" if predicted_hours <= sla_target else "At Risk",
            "reason": (
                f"{category.upper()} skill "
                f"{'matched' if skill_score else 'not found'}; "
                f"{workload:.1f} hours current workload."
            ),
        })

    ranked = sorted(results, key=lambda item: item["total_score"], reverse=True)

    return {
        "ticket_id": ticket.get("ticket_id", "Dataverse ticket"),
        "recommendation": ranked[0],
        "alternatives": ranked[1:],
        "human_review_required": True,
        "decision_note": "MVP recommendation only. A manager approves or overrides assignment.",
    }


@app.route(route="health", methods=["GET"])
def health(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(
        json.dumps({"status": "ok", "mode": "MVP sample data"}),
        mimetype="application/json",
    )


@app.route(route="recommend", methods=["POST"])
def recommend(req: func.HttpRequest) -> func.HttpResponse:
    try:
        ticket = req.get_json()

        if not ticket.get("category") or not ticket.get("priority"):
            return func.HttpResponse(
                json.dumps({"error": "category and priority are required."}),
                status_code=400,
                mimetype="application/json",
            )

        return func.HttpResponse(
            json.dumps(calculate_recommendation(ticket)),
            mimetype="application/json",
        )

    except ValueError as error:
        return func.HttpResponse(
            json.dumps({"error": str(error)}),
            status_code=400,
            mimetype="application/json",
        )
    except Exception:
        logging.exception("Ticket recommendation failed")
        return func.HttpResponse(
            json.dumps({"error": "Unable to calculate recommendation."}),
            status_code=500,
            mimetype="application/json",
        )