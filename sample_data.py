"""Safe, fictional data used by the local MVP."""

ENGINEERS = [
    {
        "id": "eng-001",
        "name": "Jordan Lee",
        "team": "Network Support",
        "skills": ["vpn", "network", "azure"],
        "open_effort_hours": 2.0,
        "available": True,
    },
    {
        "id": "eng-002",
        "name": "Priya Patel",
        "team": "Identity & Access",
        "skills": ["iam", "mfa", "azure", "access"],
        "open_effort_hours": 3.5,
        "available": True,
    },
    {
        "id": "eng-003",
        "name": "Morgan Chen",
        "team": "Workplace Support",
        "skills": ["email", "device", "m365", "teams"],
        "open_effort_hours": 1.0,
        "available": True,
    },
    {
        "id": "eng-004",
        "name": "Sam Rivera",
        "team": "Network Support",
        "skills": ["vpn", "network"],
        "open_effort_hours": 7.5,
        "available": True,
    },
]

TICKETS = [
    {
        "id": "INC001",
        "summary": "VPN connection fails before a client meeting",
        "category": "vpn",
        "priority": "P2",
        "business_impact": "Client meeting at risk",
        "created_at": "2026-08-16T09:30:00",
    },
    {
        "id": "INC002",
        "summary": "New employee cannot enroll in MFA",
        "category": "iam",
        "priority": "P3",
        "business_impact": "New starter cannot access Microsoft 365",
        "created_at": "2026-08-16T10:00:00",
    },
    {
        "id": "INC003",
        "summary": "Teams meetings fail to launch on laptop",
        "category": "m365",
        "priority": "P3",
        "business_impact": "Employee collaboration disrupted",
        "created_at": "2026-08-16T10:15:00",
    },
]
