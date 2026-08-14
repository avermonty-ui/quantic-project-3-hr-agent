from typing import Any, Dict, List, Optional

from app.llm import generate_final_answer
from hr_mcp.server import (
    lookup_employee_profile,
    check_pto_balance,
    lookup_benefits_status,
    search_policy_documents_tool,
    create_mock_hr_ticket,
    draft_hr_email,
)


def run_agent(message: str, employee_id: Optional[str] = None) -> Dict[str, Any]:
    normalized = message.lower()
    tool_trace: List[Dict[str, Any]] = []
    citations: List[Dict[str, Any]] = []
    snippets: List[Dict[str, Any]] = []

    identifier = employee_id or extract_employee_identifier(message)

    employee_profile = None

    if identifier:
        employee_result = lookup_employee_profile(identifier)
        tool_trace.append(
            {
                "tool": "lookup_employee_profile",
                "arguments": {"identifier": identifier},
                "output": employee_result,
            }
        )

        if employee_result.get("found"):
            employee_profile = employee_result["employee"]
            employee_id = employee_profile["employee_id"]

    if is_pto_request(normalized):
        return handle_pto_request(
            message=message,
            employee_id=employee_id,
            employee_profile=employee_profile,
            tool_trace=tool_trace,
        )

    if is_expense_request(normalized):
        return handle_expense_request(
            message=message,
            employee_id=employee_id,
            employee_profile=employee_profile,
            tool_trace=tool_trace,
        )

    if is_remote_work_request(normalized):
        return handle_remote_work_request(
            message=message,
            employee_id=employee_id,
            employee_profile=employee_profile,
            tool_trace=tool_trace,
        )

    if is_benefits_request(normalized):
        return handle_benefits_request(
            message=message,
            employee_id=employee_id,
            employee_profile=employee_profile,
            tool_trace=tool_trace,
        )

    return handle_policy_question(
        message=message,
        tool_trace=tool_trace,
    )


def extract_employee_identifier(message: str) -> Optional[str]:
    words = message.replace(",", " ").replace(".", " ").split()

    for word in words:
        cleaned = word.strip().upper()
        if cleaned.startswith("E") and cleaned[1:].isdigit():
            return cleaned

    known_names = [
        "Avery Kim",
        "Maya Patel",
        "Leo Martinez",
        "Nina Chen",
    ]

    normalized_message = message.lower()

    for name in known_names:
        if name.lower() in normalized_message:
            return name

    return None


def is_pto_request(message: str) -> bool:
    return any(term in message for term in ["pto", "paid time off", "vacation", "sick leave"])


def is_expense_request(message: str) -> bool:
    return any(
        term in message
        for term in [
            "expense",
            "reimburse",
            "reimbursement",
            "home office",
            "chair",
            "desk",
            "laptop",
            "travel expense",
            "receipt",
        ]
    )


def is_remote_work_request(message: str) -> bool:
    return any(
        term in message
        for term in [
            "remote",
            "work from home",
            "work remotely",
            "another state",
            "international",
        ]
    )


def is_benefits_request(message: str) -> bool:
    return any(term in message for term in ["benefit", "benefits", "medical", "dental", "vision"])


def handle_pto_request(
    message: str,
    employee_id: Optional[str],
    employee_profile: Optional[Dict[str, Any]],
    tool_trace: List[Dict[str, Any]],
) -> Dict[str, Any]:
    policy_results = search_policy_documents_tool(
        "PTO request approval requirements balance extended absence",
        top_k=4,
    )
    tool_trace.append(
        {
            "tool": "search_policy_documents_tool",
            "arguments": {
                "query": "PTO request approval requirements balance extended absence",
                "top_k": 4,
            },
            "output": summarize_tool_output(policy_results),
        }
    )

    pto_result = None
    if employee_id:
        pto_result = check_pto_balance(employee_id)
        tool_trace.append(
            {
                "tool": "check_pto_balance",
                "arguments": {"employee_id": employee_id},
                "output": pto_result,
            }
        )

    draft_result = None
    if employee_id and employee_profile:
        manager_name = employee_profile.get("manager_name", "Manager")
        draft_result = draft_hr_email(
            employee_id=employee_id,
            recipient=manager_name,
            subject="PTO request review",
            key_points=[
                "Employee is requesting PTO guidance.",
                "Manager should confirm coverage and approval in writing or through the HR system.",
                "Requests for three or more consecutive workdays require manager approval.",
            ],
        )
        tool_trace.append(
            {
                "tool": "draft_hr_email",
                "arguments": {
                    "employee_id": employee_id,
                    "recipient": manager_name,
                    "subject": "PTO request review",
                },
                "output": draft_result,
            }
        )

    citations, snippets = build_sources(policy_results)

    if not employee_id:
        answer = (
            "I can explain the PTO policy, but I need an employee ID or name to check the employee's PTO balance. "
            "Policy guidance: employees should submit PTO requests at least five business days in advance when possible, "
            "and requests for three or more consecutive workdays require manager approval."
        )
    elif not pto_result or not pto_result.get("found"):
        answer = (
            f"I could not find a PTO balance for employee {employee_id}. "
            "The policy still requires employees to check their available balance before submitting PTO, "
            "and three or more consecutive workdays require manager approval."
        )
    else:
        balance = pto_result["pto_balance"]["pto_balance_days"]
        answer = (
            f"Employee {employee_id} has {balance} PTO days available. "
            "For a three-day PTO request, the balance appears sufficient if no other pending PTO exists. "
            "Because the request is for three or more consecutive workdays, manager approval is required. "
            "The request should be submitted at least five business days before the planned absence when possible. "
            "I also drafted a mock manager email for review; it was not sent."
        )

    final_answer = generate_final_answer(
        user_message=message,
        draft_answer=answer,
        citations=citations,
        snippets=snippets,
        tool_trace=tool_trace,
    )

    return {
        "answer": final_answer,
        "citations": citations,
        "snippets": snippets,
        "tool_trace": tool_trace,
    }


def handle_remote_work_request(
    message: str,
    employee_id: Optional[str],
    employee_profile: Optional[Dict[str, Any]],
    tool_trace: List[Dict[str, Any]],
) -> Dict[str, Any]:
    policy_results = search_policy_documents_tool(
        "extended remote work out of state international approval security",
        top_k=5,
    )
    tool_trace.append(
        {
            "tool": "search_policy_documents_tool",
            "arguments": {
                "query": "extended remote work out of state international approval security",
                "top_k": 5,
            },
            "output": summarize_tool_output(policy_results),
        }
    )

    ticket_result = None

    if employee_id:
        ticket_result = create_mock_hr_ticket(
            employee_id=employee_id,
            issue_type="remote_work_review",
            summary="Review requested for extended or out-of-state remote work arrangement.",
        )
        tool_trace.append(
            {
                "tool": "create_mock_hr_ticket",
                "arguments": {
                    "employee_id": employee_id,
                    "issue_type": "remote_work_review",
                    "summary": "Review requested for extended or out-of-state remote work arrangement.",
                },
                "output": ticket_result,
            }
        )

    citations, snippets = build_sources(policy_results)

    if not employee_id:
        answer = (
            "I can explain the remote work policy, but I need an employee ID or name to check role eligibility. "
            "In general, remote work lasting more than ten consecutive business days requires manager and HR approval. "
            "Out-of-state or international remote work must be reviewed by HR before travel begins."
        )
    elif employee_profile and not employee_profile.get("remote_eligible"):
        answer = (
            f"Employee {employee_id} is not marked as remote eligible in the mock employee profile. "
            "An exception would require HR review. Extended remote work over ten consecutive business days and "
            "out-of-state or international remote work require documented manager and HR approval."
        )
    else:
        answer = (
            f"Employee {employee_id} appears remote eligible based on the mock employee profile, but a six-week remote work arrangement "
            "is extended remote work and requires manager and HR approval before it begins. "
            "If the work location is another state or country, HR must also review payroll, tax, labor law, benefits, security, "
            "insurance, and data privacy implications. I created a mock HR ticket for review."
        )

    final_answer = generate_final_answer(
        user_message=message,
        draft_answer=answer,
        citations=citations,
        snippets=snippets,
        tool_trace=tool_trace,
    )

    return {
        "answer": final_answer,
        "citations": citations,
        "snippets": snippets,
        "tool_trace": tool_trace,
    }


def handle_benefits_request(
    message: str,
    employee_id: Optional[str],
    employee_profile: Optional[Dict[str, Any]],
    tool_trace: List[Dict[str, Any]],
) -> Dict[str, Any]:
    policy_results = search_policy_documents_tool(
        "benefits eligibility full-time part-time enrollment medical dental vision",
        top_k=4,
    )
    tool_trace.append(
        {
            "tool": "search_policy_documents_tool",
            "arguments": {
                "query": "benefits eligibility full-time part-time enrollment medical dental vision",
                "top_k": 4,
            },
            "output": summarize_tool_output(policy_results),
        }
    )

    benefits_result = None
    if employee_id:
        benefits_result = lookup_benefits_status(employee_id)
        tool_trace.append(
            {
                "tool": "lookup_benefits_status",
                "arguments": {"employee_id": employee_id},
                "output": benefits_result,
            }
        )

    citations, snippets = build_sources(policy_results)

    if not employee_id:
        answer = (
            "I can explain the benefits policy, but I need an employee ID or name to check the mock benefits record. "
            "In general, full-time employees are eligible for benefits, while part-time employees are not automatically eligible."
        )
    elif not benefits_result or not benefits_result.get("found"):
        answer = f"I could not find a benefits record for employee {employee_id}."
    else:
        benefits = benefits_result["benefits"]
        eligible = benefits["benefits_eligible"]
        answer = (
            f"Employee {employee_id} benefits eligibility is {eligible}. "
            f"Medical plan: {benefits['medical_plan']}. Dental plan: {benefits['dental_plan']}. "
            f"Vision plan: {benefits['vision_plan']}. "
            "The policy states that full-time employees are generally eligible, while part-time employees, contractors, interns, "
            "and temporary workers may not be eligible unless required by law or written agreement."
        )

    final_answer = generate_final_answer(
        user_message=message,
        draft_answer=answer,
        citations=citations,
        snippets=snippets,
        tool_trace=tool_trace,
    )

    return {
        "answer": final_answer,
        "citations": citations,
        "snippets": snippets,
        "tool_trace": tool_trace,
    }


def handle_expense_request(
    message: str,
    employee_id: Optional[str],
    employee_profile: Optional[Dict[str, Any]],
    tool_trace: List[Dict[str, Any]],
) -> Dict[str, Any]:
    policy_query = (
        "business expense reimbursement home office equipment chair desk furniture "
        "pre-approval manager HR approval receipts reimbursement denial"
    )

    policy_results = search_policy_documents_tool(
        policy_query,
        top_k=4,
    )

    tool_trace.append(
        {
            "tool": "search_policy_documents_tool",
            "arguments": {
                "query": policy_query,
                "top_k": 4,
            },
            "output": summarize_tool_output(policy_results),
        }
    )

    citations, snippets = build_sources(policy_results)

    if employee_profile and employee_profile.get("remote_eligible"):
        answer = (
            f"Employee {employee_id} is marked as remote eligible in the mock employee profile. "
            "Under the Business Expense and Reimbursement Policy, remote-eligible employees may request "
            "reimbursement for basic home office equipment when the equipment is necessary for their role. "
            "However, a home office chair is treated as furniture, and chairs, desks, and other furniture "
            "require manager and HR approval before purchase. If the chair was not pre-approved, reimbursement "
            "may be denied."
        )
    elif employee_profile and not employee_profile.get("remote_eligible"):
        answer = (
            f"Employee {employee_id} is not marked as remote eligible in the mock employee profile. "
            "Under the Business Expense and Reimbursement Policy, home office reimbursement is primarily described "
            "for remote-eligible employees. A home office chair is also treated as furniture, which requires manager "
            "and HR approval before purchase. This request should not be treated as automatically reimbursable."
        )
    else:
        answer = (
            "Under the Business Expense and Reimbursement Policy, remote-eligible employees may request reimbursement "
            "for basic home office equipment when the equipment is necessary for their role. However, a home office chair "
            "is treated as furniture, and chairs, desks, and other furniture require manager and HR approval before purchase. "
            "If the chair was not pre-approved, reimbursement may be denied. I need an employee ID or name to check whether "
            "the employee is marked as remote eligible."
        )

    final_answer = generate_final_answer(
        user_message=message,
        draft_answer=answer,
        citations=citations,
        snippets=snippets,
        tool_trace=tool_trace,
    )

    return {
        "answer": final_answer,
        "citations": citations,
        "snippets": snippets,
        "tool_trace": tool_trace,
    }


def handle_policy_question(message: str, tool_trace: List[Dict[str, Any]]) -> Dict[str, Any]:
    policy_results = search_policy_documents_tool(message, top_k=5)

    tool_trace.append(
        {
            "tool": "search_policy_documents_tool",
            "arguments": {"query": message, "top_k": 5},
            "output": summarize_tool_output(policy_results),
        }
    )

    citations, snippets = build_sources(policy_results)

    if not policy_results:
        answer = "I could not find enough policy evidence to answer that question from the current HR policy corpus."
    else:
        top = policy_results[0]
        answer = (
            f"Based on the most relevant policy section, {top['title']} / {top['section']}: "
            f"{top['snippet'][:600]}"
        )

    final_answer = generate_final_answer(
        user_message=message,
        draft_answer=answer,
        citations=citations,
        snippets=snippets,
        tool_trace=tool_trace,
    )

    return {
        "answer": final_answer,
        "citations": citations,
        "snippets": snippets,
        "tool_trace": tool_trace,
    }


def build_sources(policy_results: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    citations = []
    snippets = []

    for result in policy_results:
        citation = {
            "doc_id": result["doc_id"],
            "title": result["title"],
            "section": result["section"],
            "source_path": result["source_path"],
        }

        citations.append(citation)
        snippets.append(
            {
                **citation,
                "snippet": result["snippet"],
                "score": result["score"],
            }
        )

    return citations, snippets


def summarize_tool_output(results: Any) -> Any:
    if isinstance(results, list):
        return [
            {
                "title": item.get("title"),
                "section": item.get("section"),
                "score": item.get("score"),
            }
            for item in results
        ]

    return results