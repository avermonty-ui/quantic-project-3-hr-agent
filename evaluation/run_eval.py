import json
import statistics
import time
from pathlib import Path
from typing import Any, Dict, List

from app.agent import run_agent


EVAL_FILE = Path("evaluation/eval_questions.json")
RESULTS_FILE = Path("evaluation/results.md")


def load_eval_questions() -> List[Dict[str, Any]]:
    return json.loads(EVAL_FILE.read_text(encoding="utf-8"))


def contains_any_tool(tool_trace: List[Dict[str, Any]], expected_tool: str) -> bool:
    return any(step.get("tool") == expected_tool for step in tool_trace)


def citation_titles(result: Dict[str, Any]) -> List[str]:
    return [citation.get("title", "") for citation in result.get("citations", [])]


def evaluate_question(question: Dict[str, Any]) -> Dict[str, Any]:
    start = time.perf_counter()

    result = run_agent(
        message=question["question"],
        employee_id=question.get("employee_identifier"),
    )

    latency_ms = round((time.perf_counter() - start) * 1000, 2)

    expected_tools = question.get("expected_tools", [])
    expected_sources = question.get("expected_policy_sources", [])

    tool_trace = result.get("tool_trace", [])
    citations = citation_titles(result)
    answer = result.get("answer", "")

    tool_matches = [
        tool for tool in expected_tools
        if contains_any_tool(tool_trace, tool)
    ]

    source_matches = [
        source for source in expected_sources
        if source in citations
    ]

    tool_selection_score = len(tool_matches) / len(expected_tools) if expected_tools else 1.0
    citation_score = len(source_matches) / len(expected_sources) if expected_sources else 1.0

    groundedness_score = 1.0 if result.get("citations") else 0.0

    workflow_completion_score = 1.0
    if question["category"] in [
        "pto_workflow",
        "remote_work_workflow",
        "benefits_workflow",
        "expense_workflow",
        "agentic_task",
    ]:
        workflow_completion_score = 1.0 if tool_selection_score >= 0.66 else 0.0

    return {
        "id": question["id"],
        "category": question["category"],
        "question": question["question"],
        "latency_ms": latency_ms,
        "answer": answer,
        "expected_tools": expected_tools,
        "tools_used": [step.get("tool") for step in tool_trace],
        "tool_selection_score": round(tool_selection_score, 2),
        "expected_sources": expected_sources,
        "citation_titles": citations,
        "citation_score": round(citation_score, 2),
        "groundedness_score": groundedness_score,
        "workflow_completion_score": workflow_completion_score,
    }


def summarize_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    latencies = [result["latency_ms"] for result in results]

    return {
        "question_count": len(results),
        "avg_tool_selection_score": round(statistics.mean(r["tool_selection_score"] for r in results), 2),
        "avg_citation_score": round(statistics.mean(r["citation_score"] for r in results), 2),
        "avg_groundedness_score": round(statistics.mean(r["groundedness_score"] for r in results), 2),
        "avg_workflow_completion_score": round(statistics.mean(r["workflow_completion_score"] for r in results), 2),
        "latency_p50_ms": round(statistics.median(latencies), 2),
        "latency_p95_ms": round(percentile(latencies, 95), 2),
    }


def percentile(values: List[float], percentile_value: int) -> float:
    sorted_values = sorted(values)
    index = int(round((percentile_value / 100) * (len(sorted_values) - 1)))
    return sorted_values[index]


def write_results_markdown(results: List[Dict[str, Any]], summary: Dict[str, Any]) -> None:
    lines = [
        "# Evaluation Results",
        "",
        "This evaluation set measures the HR agent across policy Q&A, multi-document retrieval, tool-requiring workflows, ambiguous requests, out-of-scope requests, and safety/escalation scenarios.",
        "",
        "## Summary Metrics",
        "",
        f"- Questions evaluated: {summary['question_count']}",
        f"- Average tool selection score: {summary['avg_tool_selection_score']}",
        f"- Average citation score: {summary['avg_citation_score']}",
        f"- Average groundedness score: {summary['avg_groundedness_score']}",
        f"- Average workflow completion score: {summary['avg_workflow_completion_score']}",
        f"- Latency p50: {summary['latency_p50_ms']} ms",
        f"- Latency p95: {summary['latency_p95_ms']} ms",
        "",
        "## Per-Question Results",
        "",
        "| ID | Category | Tool Score | Citation Score | Groundedness | Workflow | Latency ms |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]

    for result in results:
        lines.append(
            f"| {result['id']} | {result['category']} | "
            f"{result['tool_selection_score']} | "
            f"{result['citation_score']} | "
            f"{result['groundedness_score']} | "
            f"{result['workflow_completion_score']} | "
            f"{result['latency_ms']} |"
        )

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Scores are heuristic and based on expected tool names, expected citation titles, and presence of citations.",
            "- Groundedness is estimated by whether the response includes policy citations.",
            "- Workflow completion is estimated by whether the required workflow tools were selected.",
            "- Manual review should supplement these automated scores for final reporting.",
        ]
    )

    RESULTS_FILE.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    questions = load_eval_questions()
    results = []

    for question in questions:
        print(f"Evaluating {question['id']}: {question['question']}")
        results.append(evaluate_question(question))

    summary = summarize_results(results)
    write_results_markdown(results, summary)

    print("\nEvaluation complete.")
    print(json.dumps(summary, indent=2))
    print(f"\nWrote results to {RESULTS_FILE}")


if __name__ == "__main__":
    main()