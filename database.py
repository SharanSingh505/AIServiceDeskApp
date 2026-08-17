"""Small local SQLite store for the MVP; no external service is required."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from sample_data import ENGINEERS, TICKETS

DB_PATH = Path(__file__).parent / "service_desk.db"


def connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database() -> None:
    with connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS engineers (
              id TEXT PRIMARY KEY, name TEXT NOT NULL, team TEXT NOT NULL,
              skills_json TEXT NOT NULL, open_effort_hours REAL NOT NULL, available INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS tickets (
              id TEXT PRIMARY KEY, summary TEXT NOT NULL, category TEXT NOT NULL,
              priority TEXT NOT NULL, business_impact TEXT NOT NULL, created_at TEXT NOT NULL,
              status TEXT NOT NULL DEFAULT 'New', assigned_engineer_id TEXT,
              assigned_engineer_name TEXT
            );
        """)
        if conn.execute("SELECT COUNT(*) FROM engineers").fetchone()[0] == 0:
            conn.executemany("INSERT INTO engineers VALUES (:id, :name, :team, :skills_json, :open_effort_hours, :available)", [
                {**engineer, "skills_json": json.dumps(engineer["skills"]), "available": int(engineer["available"])}
                for engineer in ENGINEERS
            ])
        if conn.execute("SELECT COUNT(*) FROM tickets").fetchone()[0] == 0:
            conn.executemany("""INSERT INTO tickets (id, summary, category, priority, business_impact, created_at, status)
                VALUES (:id, :summary, :category, :priority, :business_impact, :created_at, 'New')""", TICKETS)


def _engineer(row: sqlite3.Row) -> dict:
    data = dict(row)
    data["skills"] = json.loads(data.pop("skills_json"))
    data["available"] = bool(data["available"])
    return data


def list_engineers() -> list[dict]:
    with connection() as conn:
        return [_engineer(row) for row in conn.execute("SELECT * FROM engineers ORDER BY name")]


def list_tickets() -> list[dict]:
    with connection() as conn:
        return [dict(row) for row in conn.execute("SELECT * FROM tickets ORDER BY id")]


def get_ticket(ticket_id: str) -> dict | None:
    with connection() as conn:
        row = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
        return dict(row) if row else None


def get_engineer(engineer_id: str) -> dict | None:
    with connection() as conn:
        row = conn.execute("SELECT * FROM engineers WHERE id = ?", (engineer_id,)).fetchone()
        return _engineer(row) if row else None


def create_ticket(ticket: dict) -> dict:
    with connection() as conn:
        next_number = conn.execute("SELECT COUNT(*) FROM tickets").fetchone()[0] + 1
        record = {"id": f"INC{next_number:03d}", "status": "New", "assigned_engineer_id": None,
                  "assigned_engineer_name": None, **ticket}
        conn.execute("""INSERT INTO tickets VALUES (:id, :summary, :category, :priority, :business_impact,
                    :created_at, :status, :assigned_engineer_id, :assigned_engineer_name)""", record)
        return record


def assign_ticket(ticket_id: str, engineer: dict) -> dict | None:
    with connection() as conn:
        conn.execute("""UPDATE tickets SET status = 'Assigned', assigned_engineer_id = ?, assigned_engineer_name = ?
                    WHERE id = ?""", (engineer["id"], engineer["name"], ticket_id))
        row = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
        return dict(row) if row else None
