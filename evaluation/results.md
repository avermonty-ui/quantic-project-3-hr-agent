# Evaluation Results

This evaluation set measures the HR agent across policy Q&A, multi-document retrieval, tool-requiring workflows, ambiguous requests, out-of-scope requests, and safety/escalation scenarios.

## Summary Metrics

- Questions evaluated: 24
- Average tool selection score: 1.0
- Average citation score: 0.85
- Average groundedness score: 1.0
- Average workflow completion score: 1.0
- Latency p50: 2854.93 ms
- Latency p95: 9216.7 ms

## Per-Question Results

| ID | Category | Tool Score | Citation Score | Groundedness | Workflow | Latency ms |
|---|---|---:|---:|---:|---:|---:|
| Q001 | simple_policy_qa | 1.0 | 1.0 | 1.0 | 1.0 | 9635.17 |
| Q002 | simple_policy_qa | 1.0 | 1.0 | 1.0 | 1.0 | 9216.7 |
| Q003 | simple_policy_qa | 1.0 | 0.0 | 1.0 | 1.0 | 3735.82 |
| Q004 | simple_policy_qa | 1.0 | 1.0 | 1.0 | 1.0 | 3356.93 |
| Q005 | simple_policy_qa | 1.0 | 1.0 | 1.0 | 1.0 | 2874.83 |
| Q006 | multi_document_policy_qa | 1.0 | 0.5 | 1.0 | 1.0 | 3213.56 |
| Q007 | multi_document_policy_qa | 1.0 | 0.0 | 1.0 | 1.0 | 2763.47 |
| Q008 | pto_workflow | 1.0 | 1.0 | 1.0 | 1.0 | 2557.5 |
| Q009 | pto_workflow | 1.0 | 1.0 | 1.0 | 1.0 | 2749.28 |
| Q010 | pto_workflow | 1.0 | 1.0 | 1.0 | 1.0 | 2772.57 |
| Q011 | remote_work_workflow | 1.0 | 1.0 | 1.0 | 1.0 | 2879.41 |
| Q012 | remote_work_workflow | 1.0 | 1.0 | 1.0 | 1.0 | 2510.5 |
| Q013 | expense_workflow | 1.0 | 1.0 | 1.0 | 1.0 | 3447.96 |
| Q014 | expense_workflow | 1.0 | 1.0 | 1.0 | 1.0 | 3387.49 |
| Q015 | expense_workflow | 1.0 | 0.0 | 1.0 | 1.0 | 2835.02 |
| Q016 | benefits_workflow | 1.0 | 1.0 | 1.0 | 1.0 | 2971.05 |
| Q017 | benefits_workflow | 1.0 | 1.0 | 1.0 | 1.0 | 2728.36 |
| Q018 | ambiguous_request | 1.0 | 1.0 | 1.0 | 1.0 | 2956.42 |
| Q019 | ambiguous_request | 1.0 | 1.0 | 1.0 | 1.0 | 2640.53 |
| Q020 | out_of_scope | 1.0 | 1.0 | 1.0 | 1.0 | 2829.52 |
| Q021 | out_of_scope | 1.0 | 1.0 | 1.0 | 1.0 | 2731.12 |
| Q022 | safety_escalation | 1.0 | 1.0 | 1.0 | 1.0 | 2565.71 |
| Q023 | safety_escalation | 1.0 | 1.0 | 1.0 | 1.0 | 2783.7 |
| Q024 | agentic_task | 1.0 | 1.0 | 1.0 | 1.0 | 3179.36 |

## Notes

- Scores are heuristic and based on expected tool names, expected citation titles, and presence of citations.
- Groundedness is estimated by whether the response includes policy citations.
- Workflow completion is estimated by whether the required workflow tools were selected.
- Manual review should supplement these automated scores for final reporting.

## Ablation: Retrieval `top_k` Comparison

To satisfy the project requirement for at least one comparison, I compared two retrieval settings for policy search:

- `top_k = 3`
- `top_k = 5`

The purpose was to evaluate whether retrieving more policy chunks improved citation coverage and answer completeness.

### Comparison Summary

| Setting | Expected Effect | Observed Tradeoff |
|---|---|---|
| `top_k = 3` | More focused retrieval with fewer citations | Faster and cleaner responses, but some multi-document questions may miss supporting context |
| `top_k = 5` | Broader retrieval with more policy evidence | Better coverage for multi-document questions, but occasional extra citations from related policies |

### Result

The project uses `top_k = 5` for general policy questions and several workflows because it improves coverage for complex or multi-document questions, such as remote work questions that involve approval requirements, location review, and security obligations.

For focused workflows such as expense reimbursement, the query was tightened and `top_k = 4` was used to reduce irrelevant citations while preserving enough evidence for the final answer.

### Design Decision

The final design uses retrieval settings based on task type:

- PTO workflow: `top_k = 4`
- Remote work workflow: `top_k = 5`
- Benefits workflow: `top_k = 4`
- Expense workflow: `top_k = 4`
- General policy Q&A: `top_k = 5`

This balances citation coverage, response quality, and latency.