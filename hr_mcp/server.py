from pathlib import Path
from typing import Any, Dict, List, Optional
import json

from fastmcp import FastMCP

from rag.retriever import search_policy_documents


mcp = FastMCP("hr-policy-tools")

DATA_DIR = Path("mock_data")


def load_json(filename: str) -> Any:
    path = DATA_DIR / filename
    return json.loads(path.read_text(encoding="utf-8"))


def find_by_employee_id(filename: str, employee_id: str) -> Optional[Dict]:
    records = load_json(filename)

    for record in records:
        if record.get("employee_id") == employee_id:
            return record

    return None


@mcp.tool()
def search_policy_documents_tool(query: str, top_k: int = 5) -> List[Dict]:
    """Search HR policy documents and return relevant policy evidence."""
    return search_policy_documents(query=query, top_k=top_k)


@mcp.tool()
def lookup_employee_profile(employee_id: str) -> Dict:
    """Look up a synthetic employee profile by employee ID."""
    employee = find_by_employee_id("employees.json", employee_id)

    if not employee:
        return {
            "found": False,
            "employee_id": employee_id,
            "message": "No employee profile found for this employee ID."
        }

    return {
        "found": True,
        "employee": employee
    }


@mcp.tool()
def check_pto_balance(employee_id: str) -> Dict:
    """Check a synthetic employee's PTO, sick leave, and floating holiday balances."""
    balance = find_by_employee_id("pto_balances.json", employee_id)

    if not balance:
        return {
            "found": False,
            "employee_id": employee_id,
            "message": "No PTO balance found for this employee ID."
        }

    return {
        "found": True,
        "pto_balance": balance
    }


@mcp.tool()
def lookup_benefits_status(employee_id: str) -> Dict:
    """Look up a synthetic employee's benefits eligibility and elections."""
    benefits = find_by_employee_id("benefits.json", employee_id)

    if not benefits:
        return {
            "found": False,
            "employee_id": employee_id,
            "message": "No benefits record found for this employee ID."
        }

    return {
        "found": True,
        "benefits": benefits
    }


@mcp.tool()
def create_mock_hr_ticket(employee_id: str, issue_type: str, summary: str) -> Dict:
    """Create a mock HR ticket. This is a simulated action only."""
    tickets = load_json("tickets.json")

    ticket_id = f"T{len(tickets) + 1:04d}"

    ticket = {
        "ticket_id": ticket_id,
        "employee_id": employee_id,
        "issue_type": issue_type,
        "summary": summary,
        "status": "mock_created",
        "note": "This is a simulated HR ticket for project demonstration only."
    }

    tickets.append(ticket)

    path = DATA_DIR / "tickets.json"
    path.write_text(json.dumps(tickets, indent=2), encoding="utf-8")

    return {
        "created": True,
        "ticket": ticket
    }


@mcp.tool()
def draft_hr_email(employee_id: str, recipient: str, subject: str, key_points: List[str]) -> Dict:
    """Draft a mock HR email. This does not send an email."""
    employee = find_by_employee_id("employees.json", employee_id)

    employee_name = employee["name"] if employee else employee_id

    body = (
        f"Hello {recipient},\n\n"
        f"I am writing regarding {employee_name} ({employee_id}).\n\n"
        "Key points:\n"
        + "\n".join([f"- {point}" for point in key_points])
        + "\n\nPlease review and advise on next steps.\n\n"
        "Thank you."
    )

    return {
        "drafted": True,
        "email": {
            "to": recipient,
            "subject": subject,
            "body": body
        },
        "note": "This is a draft only and was not sent."
    }


if __name__ == "__main__":
    mcp.run()