from hr_mcp.server import (
    lookup_employee_profile,
    check_pto_balance,
    lookup_benefits_status,
    search_policy_documents_tool,
)


def test_lookup_employee_profile():
    result = lookup_employee_profile("E1001")
    assert result["found"] is True
    assert result["employee"]["name"] == "Avery Kim"


def test_check_pto_balance():
    result = check_pto_balance("E1001")
    assert result["found"] is True
    assert result["pto_balance"]["pto_balance_days"] == 12


def test_lookup_benefits_status():
    result = lookup_benefits_status("E1003")
    assert result["found"] is True
    assert result["benefits"]["benefits_eligible"] is False


def test_search_policy_documents_tool():
    result = search_policy_documents_tool("PTO approval requirements", top_k=2)
    assert len(result) > 0
    assert "title" in result[0]
    assert "snippet" in result[0]

def test_lookup_employee_profile_by_name():
    result = lookup_employee_profile("Avery Kim")
    assert result["found"] is True
    assert result["employee"]["employee_id"] == "E1001"

def test_lookup_employee_profile():
    result = lookup_employee_profile("E1001")
    assert result["found"] is True
    assert result["employee"]["name"] == "Avery Kim"