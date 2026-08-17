"""Optional Dataverse mapping helpers for the Service Desk MVP."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class DataverseSettings:
    url: str
    tenant_id: str
    client_id: str
    client_secret: str
    tickets_entity_set: str = "crf96_servicedesktickets"

    @classmethod
    def from_environment(cls) -> "DataverseSettings | None":
        values = {
            "url": os.getenv("DATAVERSE_URL", "").rstrip("/"),
            "tenant_id": os.getenv("ENTRA_TENANT_ID", ""),
            "client_id": os.getenv("ENTRA_CLIENT_ID", ""),
            "client_secret": os.getenv("ENTRA_CLIENT_SECRET", ""),
            "tickets_entity_set": os.getenv("DATAVERSE_TICKETS_ENTITY_SET", "crf96_servicedesktickets"),
        }
        needed = ("url", "tenant_id", "client_id", "client_secret")
        return cls(**values) if all(values[key] for key in needed) else None


def dataverse_to_ticket(record: dict[str, Any]) -> dict[str, Any]:
    """Map Dataverse columns to the Python recommendation engine format."""
    priority = record.get("crf96_priority") or "P3 - Medium"
    return {
        "id": record.get("crf96_servicedeskticketid", ""),
        "ticket_number": record.get("crf96_ticketnumber", ""),
        "summary": record.get("crf96_summary", ""),
        "category": record.get("crf96_category@OData.Community.Display.V1.FormattedValue", ""),
        "priority": priority[:2],
        "status": record.get("crf96_status@OData.Community.Display.V1.FormattedValue", "New"),
        "business_impact": record.get("crf96_businessimpact", "Standard user impact"),
    }


def configuration_message() -> str:
    if DataverseSettings.from_environment() is None:
        return "Dataverse connector not configured; using the local MVP database."
    return "Dataverse connector configuration detected."
