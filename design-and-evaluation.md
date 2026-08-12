# Design and Evaluation

## Project Overview

Northstar PeopleOps Assistant is an agentic HR policy and operations assistant. It combines a policy RAG system, MCP-style tool calls, synthetic HR data, and a FastAPI web application.

The system supports HR policy Q&A and multi-step HR workflows involving employee profile lookup, PTO balances, benefits status, remote work review, mock HR ticket creation, and mock HR email drafting.

The application is designed for a free-tier single-service deployment where the web app, agent orchestration layer, RAG retriever, Chroma vector store, mock HR data, and MCP-style tools run together.

## Architecture

```text
User
  |
  v
FastAPI Web App
  |
  |-- GET /
  |-- GET /health
  |-- POST /chat
  |
  v
Agent Orchestrator
  |
  |-- Intent routing
  |-- Tool selection
  |-- Workflow execution
  |-- Citation and trace assembly
  |
  v
MCP-Style HR Tools
  |
  |-- search_policy_documents_tool
  |-- lookup_employee_profile
  |-- check_pto_balance
  |-- lookup_benefits_status
  |-- create_mock_hr_ticket
  |-- draft_hr_email
  |
  v
Data and Retrieval Layer
  |
  |-- Chroma vector store
  |-- sentence-transformers embeddings
  |-- Markdown HR policy corpus
  |-- JSON mock employee/PTO/benefits/ticket data
```

## Main Components

### Web Application

The web application is implemented with FastAPI.

Primary endpoints:

```text
GET /
GET /health
POST /chat
```

The `/` endpoint provides a branded web chat UI for Northstar People Operations. The `/health` endpoint returns basic application status. The `/chat` endpoint receives a user message and optional employee identifier, runs the agent workflow, and returns:

```text
answer
citations
snippets
tool_trace
```

### Agent Orchestrator

The agent orchestrator is implemented in:

```text
app/agent.py
```

The orchestrator performs deterministic intent routing based on the user message. It identifies whether the request is primarily about:

- PTO
- Remote work
- Benefits
- Expenses
- General policy Q&A

The agent then calls the appropriate MCP-style tools, assembles policy citations and snippets, and returns a final answer with a visible operational trace.

The system does not expose hidden chain-of-thought. The trace is an operational trace showing selected tools, tool arguments, and summarized tool outputs.

## RAG Design

### Policy Corpus

The policy corpus is stored as Markdown files in:

```text
policies/
```

Current policy documents:

```text
pto_policy.md
remote_work_policy.md
expense_policy.md
benefits_policy.md
data_security_policy.md
```

The corpus supports questions about PTO, remote work, expenses, data security, benefits, equipment/security requirements, and operational approvals.

### Ingestion

Policy ingestion is implemented in:

```text
rag/ingest.py
```

The ingestion pipeline:

1. Reads Markdown files from the `policies/` folder.
2. Extracts policy titles from top-level Markdown headings.
3. Splits documents into section-aware chunks using `##` headings.
4. Applies a maximum chunk size with overlap for longer sections.
5. Embeds chunks using a local `sentence-transformers` model.
6. Stores the embedded chunks in Chroma.
7. Preserves metadata for citation use.

### Chunking Strategy

The system uses heading-aware chunking because HR policies are naturally organized by sections such as eligibility, approval process, security requirements, and reimbursement rules.

Each chunk stores metadata:

```text
doc_id
title
section
source_path
```

This supports readable citations in the final answer.

### Embedding Model

The embedding model is:

```text
sentence-transformers/all-MiniLM-L6-v2
```

This model was selected because it is free, local, lightweight, and suitable for a small policy corpus.

### Vector Store

The vector database is ChromaDB.

The persisted vector store path is:

```text
rag/vector_store
```

The collection name is:

```text
hr_policies
```

### Retrieval

Retrieval is implemented in:

```text
rag/retriever.py
```

The retriever embeds the user query, searches the Chroma collection, and returns top-k matches with document metadata and snippets.

Different workflows use different retrieval settings:

```text
PTO workflow: top_k = 4
Remote work workflow: top_k = 5
Benefits workflow: top_k = 4
Expense workflow: top_k = 4
General policy Q&A: top_k = 5
```

This balances coverage and citation focus.

## MCP-Style Tool Design

The MCP-style tools are implemented in:

```text
hr_mcp/server.py
```

The project originally used a folder named `mcp/`, but this was renamed to `hr_mcp/` to avoid a Python import conflict with the installed `mcp` package. The architecture remains MCP-style and uses FastMCP-compatible tool definitions.

### Tool List

| Tool | Purpose |
|---|---|
| `search_policy_documents_tool` | Searches the HR policy RAG index and returns relevant policy evidence. |
| `lookup_employee_profile` | Looks up a synthetic employee profile by employee ID or exact employee name. |
| `check_pto_balance` | Checks a synthetic employee's PTO, sick leave, and floating holiday balances. |
| `lookup_benefits_status` | Looks up a synthetic employee's benefits eligibility and plan elections. |
| `create_mock_hr_ticket` | Creates a simulated HR ticket for demonstration only. |
| `draft_hr_email` | Drafts a mock HR email and does not send it. |

### Mock Structured Data

Mock structured data is stored in:

```text
mock_data/
```

Files:

```text
employees.json
pto_balances.json
benefits.json
tickets.json
```

The data is fully synthetic and does not include real employee information.

### Employee Lookup

The system supports lookup by either employee ID or exact employee name.

Examples:

```text
E1001
Avery Kim
```

This improves the user experience while preserving deterministic structured-data lookup.

## Agentic Workflows

## Workflow 1: PTO Request Guidance

Example prompt:

```text
Can Avery Kim take three days of PTO next week?
```

Expected sequence:

1. `lookup_employee_profile`
2. `check_pto_balance`
3. `search_policy_documents_tool`
4. `draft_hr_email`

The agent checks the employee profile, retrieves the PTO balance, searches the PTO policy, determines whether manager approval is required, and drafts a mock manager email.

The answer cites PTO policy sections such as:

```text
Request Requirements
PTO Balances
Approval Process
```

## Workflow 2: Extended Remote Work Review

Example prompt:

```text
Can Maya Patel work remotely from another state for six weeks?
```

Expected sequence:

1. `lookup_employee_profile`
2. `search_policy_documents_tool`
3. `create_mock_hr_ticket`

The agent checks employee eligibility, retrieves remote work policy evidence, determines that six weeks is extended remote work, identifies manager and HR approval requirements, and creates a mock HR ticket.

The answer cites remote work policy sections such as:

```text
Extended Remote Work
Out-of-State or International Remote Work
Security Requirements
```

## Additional Supported Workflow: Benefits Eligibility

Example prompt:

```text
Is Leo Martinez eligible for medical, dental, and vision benefits?
```

Expected sequence:

1. `lookup_employee_profile`
2. `lookup_benefits_status`
3. `search_policy_documents_tool`

The agent checks the employee profile and benefits record, retrieves the benefits policy, and returns a grounded eligibility answer.

## Additional Supported Workflow: Expense Reimbursement

Example prompt:

```text
Can Avery Kim expense a home office chair?
```

Expected sequence:

1. `lookup_employee_profile`
2. `search_policy_documents_tool`

The agent checks whether the employee is remote eligible, retrieves expense policy evidence, and determines whether the item requires manager and HR pre-approval.

## Safety and Guardrails

The system includes the following guardrails:

- Mock actions only: HR tickets and emails are simulated.
- No irreversible actions are performed.
- Mock emails are drafted but not sent.
- Mock HR tickets are created only in local synthetic data.
- Responses include policy citations when policy evidence is available.
- The system avoids inventing employee data when no employee identifier is provided.
- The system asks for an employee ID or name when structured data is needed.
- Out-of-scope questions are routed to policy search and should be redirected if not supported by the HR corpus.
- Hidden reasoning is not exposed; only operational tool traces are shown.

## Evaluation Design

Evaluation files are stored in:

```text
evaluation/
```

Files:

```text
eval_questions.json
run_eval.py
results.md
```

The evaluation set includes 24 questions and tasks covering:

- Simple policy Q&A
- Multi-document policy Q&A
- PTO workflows
- Remote work workflows
- Benefits workflows
- Expense workflows
- Ambiguous requests
- Out-of-scope requests
- Safety/escalation scenarios
- Agentic mock-ticket tasks

## Evaluation Metrics

The evaluation runner reports:

```text
tool selection score
citation score
groundedness score
workflow completion score
latency p50
latency p95
```

The current recorded metrics are:

```text
Questions evaluated: 24
Average tool selection score: 1.0
Average citation score: 0.85
Average groundedness score: 1.0
Average workflow completion score: 1.0
Latency p50: 2854.93 ms
Latency p95: 9216.7 ms
```

These metrics are heuristic and are based on expected tool names, expected citation titles, and presence of citations. Manual review should supplement the automated scores.

## Retrieval Ablation

The evaluation includes a retrieval comparison between:

```text
top_k = 3
top_k = 5
```

Summary:

| Setting | Expected Effect | Observed Tradeoff |
|---|---|---|
| `top_k = 3` | More focused retrieval with fewer citations | Faster and cleaner responses, but some multi-document questions may miss supporting context |
| `top_k = 5` | Broader retrieval with more policy evidence | Better coverage for multi-document questions, but occasional extra citations from related policies |

The final design uses `top_k = 5` for general and multi-document questions, while focused workflows such as expense reimbursement use tighter queries and `top_k = 4`.

## Testing

Automated tests are implemented with pytest.

Current tests cover:

- `/health`
- `/chat`
- employee lookup
- PTO balance lookup
- benefits lookup
- policy search tool
- employee lookup by name

Run tests with:

```bash
pytest
```

## CI/CD

GitHub Actions CI is configured in:

```text
.github/workflows/ci.yml
```

The workflow runs on push and pull request to `main`.

CI steps:

1. Check out repository.
2. Set up Python 3.11.
3. Install dependencies.
4. Build the RAG index.
5. Run pytest.
6. Import the FastAPI app.
7. Import and call an MCP-style tool.

This satisfies the automated build/test requirement and verifies both app startup and tool functionality.

## Deployment Architecture

The project is designed for a single-service free-tier deployment on Render, Railway, or an equivalent platform.

Deployment model:

```text
Single Web Service
  |
  |-- FastAPI app
  |-- Agent orchestrator
  |-- RAG retriever
  |-- Chroma vector store
  |-- MCP-style tools
  |-- Mock JSON data
```

A paid database is not required. Mock data is stored in committed JSON files, and the vector store can be built during deployment startup.

## Known Limitations

- The current system uses deterministic workflow logic rather than a fully autonomous planning loop.
- The mock HR ticket system writes to local JSON and is not connected to a real HR system.
- The current app does not send emails; it drafts mock emails only.
- The evaluation scores are heuristic and should be supplemented by manual inspection.
- On free-tier deployment, cold starts may increase latency.
- The RAG corpus is intentionally small for free-tier compatibility.

## Summary

Northstar PeopleOps Assistant demonstrates a working agentic HR assistant with policy RAG, structured mock data, MCP-style tool use, operational tracing, automated tests, CI, and evaluation results. The system is designed to be reproducible locally and deployable on free-tier infrastructure.