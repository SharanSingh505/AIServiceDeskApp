"""Explainable ticket-assignment and SLA-risk logic for the local MVP."""

from __future__ import annotations

from typing import Any

SLA_HOURS = {"P1": 4.0, "P2": 8.0, "P3": 24.0, "P4": 72.0}
COMPLEXITY_HOURS = {"P1": 4.0, "P2": 2.5, "P3": 1.5, "P4": 1.0}


def _normalize(value: str) -> str:
    return value.strip().lower()


def score_engineer(ticket: dict[str, Any], engineer: dict[str, Any]) -> dict[str, Any]:
    """Return transparent score components for one engineer."""
    category = _normalize(ticket["category"])
    skills = {_normalize(skill) for skill in engineer["skills"]}
    skill_match = 40 if category in skills else 0
    availability = 15 if engineer["available"] else 0
    workload = float(engineer["open_effort_hours"])
    workload_score = max(0, round(25 * (1 - workload / 8), 1))
    predicted_hours = round(COMPLEXITY_HOURS[ticket["priority"]] + workload * 0.35, 1)
    sla_hours = SLA_HOURS[ticket["priority"]]
    sla_score = 20 if predicted_hours <= sla_hours else 0
    total = round(skill_match + availability + workload_score + sla_score, 1)
    return {
        "engineer_id": engineer["id"], "engineer_name": engineer["name"],
        "team": engineer["team"], "total_score": total,
        "skill_match_score": skill_match, "availability_score": availability,
        "workload_score": workload_score, "sla_likelihood_score": sla_score,
        "open_effort_hours": workload, "predicted_resolution_hours": predicted_hours,
        "sla_target_hours": sla_hours, "likely_to_meet_sla": predicted_hours <= sla_hours,
        "reason": (f"{category.upper()} skill {'matched' if skill_match else 'not found'}; "
                   f"{workload:.1f}h current effort; predicted resolution {predicted_hours:.1f}h."),
    }


def recommend(ticket: dict[str, Any], engineers: list[dict[str, Any]]) -> dict[str, Any]:
    """Rank engineers and return the best recommendation with explanation."""
    ranked = sorted((score_engineer(ticket, engineer) for engineer in engineers), key=lambda item: item["total_score"], reverse=True)
    if not ranked:
        raise ValueError("No engineers are available to score.")
    return {"ticket_id": ticket["id"], "recommendation": ranked[0], "alternatives": ranked[1:],
            "human_review_required": True,
            "decision_note": "This is an MVP recommendation. A manager approves or overrides assignment."}
