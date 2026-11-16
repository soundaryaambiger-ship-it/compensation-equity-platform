import re

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.entities import (
    AdjustmentProposal,
    CompensationBand,
    Employee,
    Level,
    Location,
    Role,
    SalaryRecord,
)


AGENT_OVERVIEW = (
    "The six deterministic agents run in sequence: Data Quality flags invalid FTE or missing "
    "currency conversion; Normalization compares pay in INR at 1.0 FTE; Band Compliance checks "
    "effective bands and calculates compa-ratio and band position; Comparability groups by role, "
    "level, location and year; Disparity flags salaries below 80% of a group median when the group "
    "has at least 3 records; Recommendation creates a pending human-review proposal."
)


def answer_question(question: str, db: Session) -> str:
    query = question.strip()
    normalized = query.casefold()

    employee_id = re.search(r"\bEMP-\d{6}\b", query, re.IGNORECASE)
    if employee_id:
        employee = db.get(Employee, employee_id.group().upper())
        if employee:
            return f"{employee.name}'s employee ID is {employee.id}."
        return f"I couldn't find employee ID {employee_id.group().upper()} in the local database."

    if "employee" in normalized and any(word in normalized for word in ("id", "identifier")):
        name_match = re.search(r"\b(?:for|of)\s+(.+?)\s*[?.!]*$", query, re.IGNORECASE)
        if not name_match:
            return "Which synthetic employee do you mean? Include the name shown on the Employees page."
        name = name_match.group(1).strip().strip("\"'")
        employee = db.query(Employee).filter(func.lower(Employee.name) == name.casefold()).first()
        if employee:
            return f"{employee.name}'s employee ID is {employee.id}."
        return f"I couldn't find an employee named '{name}' in the local database."

    if any(word in normalized for word in ("agent", "pipeline", "orchestrator")):
        return AGENT_OVERVIEW

    if "compa-ratio" in normalized or "band position" in normalized:
        return (
            "Compa-ratio is normalized annual salary divided by the effective band midpoint. "
            "Band position is (salary − band minimum) ÷ (band maximum − band minimum); values "
            "below 0 or above 1 are outside the band."
        )

    if any(word in normalized for word in ("disparity", "pay gap", "threshold", "group median")):
        return (
            "The demo groups records by role, level, location and salary year. It flags a "
            "normalized salary below 80% of the group median when a group has at least 3 records. "
            "A flag is a prompt for human review, not proof of unfair treatment."
        )

    if any(word in normalized for word in ("currency", "normaliz", "fte", "exchange rate")):
        return (
            "The generated annualized INR value is derived from salary, the configured currency "
            "conversion and FTE. Analysis compares pay at 1.0 FTE and excludes records with "
            "missing annualized INR. Demo FX rates are synthetic and static by location."
        )

    if any(word in normalized for word in ("proposal", "approval", "approve", "reject")):
        return (
            "Analysis creates pending review proposals with evidence. An HR reviewer can approve "
            "or reject them; each decision is recorded as an audit event. The demo does not apply "
            "the proposed amount to a salary record."
        )

    asks_count = any(word in normalized for word in ("how many", "count", "number of"))
    if asks_count:
        if "employee" in normalized:
            count = db.query(func.count(Employee.id)).scalar() or 0
            return f"There are {count:,} employees in the local database."
        if "salary" in normalized:
            count = db.query(func.count(SalaryRecord.id)).scalar() or 0
            return f"There are {count:,} salary records in the local database."
        if "pending" in normalized or "proposal" in normalized or "review" in normalized:
            count = db.query(func.count(AdjustmentProposal.id)).filter(
                AdjustmentProposal.status == "PENDING"
            ).scalar() or 0
            return f"There are {count:,} pending adjustment proposals."
        if "combination" in normalized and ("role" in normalized or "level" in normalized):
            count = db.query(CompensationBand.role_id, CompensationBand.level_id).distinct().count()
            return f"There are {count:,} role/level combinations in the compensation bands."
        if "role" in normalized:
            count = db.query(func.count(Role.id)).scalar() or 0
            return f"There are {count:,} roles in the local database."
        if "level" in normalized:
            count = db.query(func.count(Level.id)).scalar() or 0
            return f"There are {count:,} levels in the local database."
        if "location" in normalized:
            count = db.query(func.count(Location.id)).scalar() or 0
            return f"There are {count:,} locations in the local database."

    return (
        "I can answer project questions and query the local synthetic database. Try asking how "
        "many employees or salary records there are, request an employee ID by name, or ask about "
        "the agents, disparity rule, normalization, bands or proposals."
    )
