# Northstar PeopleOps Assistant

Northstar PeopleOps Assistant is an agentic HR policy and operations assistant built for Quantic Project 3. The application combines Retrieval-Augmented Generation (RAG), MCP-style tool use, mock structured HR data, and a FastAPI web application.

The assistant can answer HR policy questions, retrieve supporting policy citations, look up synthetic employee records, check PTO and benefits data, create mock HR tickets, draft mock HR emails, and show a concise operational tool trace.

## Features

- Branded web chat UI
- FastAPI `/chat` endpoint
- FastAPI `/health` endpoint
- HR policy RAG over Markdown policy documents
- Chroma vector store
- Local `sentence-transformers` embedding model
- MCP-style HR tools
- Synthetic employee, PTO, benefits, and ticket data
- Agentic workflows for PTO, remote work, benefits, and expenses
- Employee lookup by employee ID or employee name
- Operational tool trace showing selected tools, arguments, and outputs
- Automated tests with `pytest`
- GitHub Actions CI
- Evaluation set with 24 questions/tasks
- Evaluation results with tool selection, citation, groundedness, workflow completion, and latency metrics

## Demo Workflows

The deployed demo focuses on two required end-to-end agentic workflows.

### Demo 1: PTO Request Guidance

Example prompt:

```text
Can Avery Kim take three days of PTO next week?
```

Expected behavior:

1. Look up Avery Kim's employee profile.
2. Check Avery Kim's PTO balance.
3. Retrieve PTO policy evidence.
4. Draft a mock manager email.
5. Return a cited answer and operational tool trace.

Expected tools:

```text
lookup_employee_profile
check_pto_balance
search_policy_documents_tool
draft_hr_email
```

### Demo 2: Extended Remote Work Review

Example prompt:

```text
Can Maya Patel work remotely from another state for six weeks?
```

Expected behavior:

1. Look up Maya Patel's employee profile.
2. Retrieve remote work policy evidence.
3. Determine that the request requires manager and HR approval.
4. Create a mock HR ticket for HR review.
5. Return a cited answer and operational tool trace.

Expected tools:

```text
lookup_employee_profile
search_policy_documents_tool
create_mock_hr_ticket
```

## Additional Supported Workflows

The app also supports additional HR policy and operations workflows.

### Benefits Eligibility Check

Example prompt:

```text
Is Leo Martinez eligible for medical, dental, and vision benefits?
```

Expected behavior:

1. Look up Leo Martinez's employee profile.
2. Look up Leo Martinez's benefits status.
3. Retrieve benefits policy evidence.
4. Return a cited answer and operational tool trace.

### Expense Reimbursement Policy Question

Example prompt:

```text
Can Avery Kim expense a home office chair?
```

Expected behavior:

1. Look up Avery Kim's employee profile.
2. Retrieve business expense policy evidence.
3. Determine whether the item is automatically reimbursable or requires pre-approval.
4. Return a cited answer and operational tool trace.

## Tech Stack

- Python 3.11 recommended
- FastAPI
- Uvicorn
- ChromaDB
- `sentence-transformers`
- FastMCP
- pytest
- GitHub Actions
- JSON mock data
- Markdown policy corpus

## Project Structure

```text
app/
  main.py
  agent.py

evaluation/
  eval_questions.json
  run_eval.py
  results.md

hr_mcp/
  server.py

mock_data/
  employees.json
  pto_balances.json
  benefits.json
  tickets.json

policies/
  pto_policy.md
  remote_work_policy.md
  expense_policy.md
  benefits_policy.md
  data_security_policy.md

rag/
  ingest.py
  retriever.py

tests/
  test_health.py
  test_mcp_tools.py

.github/workflows/
  ci.yml
```

## Local Setup

Create and activate a virtual environment.

On Git Bash for Windows:

```bash
python -m venv .venv
source .venv/Scripts/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a local `.env` file from the example:

```bash
cp .env.example .env
```

Add real API keys to `.env` if using external LLM providers. Do not commit `.env`.

## Build the RAG Index

Run:

```bash
python rag/ingest.py
```

This reads the Markdown policy files, chunks them, embeds them, and stores them in a local Chroma vector store.

## Run the Application Locally

Run:

```bash
uvicorn app.main:app --reload
```

Open the web app:

```text
http://127.0.0.1:8000/
```

API docs are available at:

```text
http://127.0.0.1:8000/docs
```

Health endpoint:

```text
http://127.0.0.1:8000/health
```

## Run Tests

Run:

```bash
pytest
```

## Run Evaluation

Run:

```bash
python -m evaluation.run_eval
```

The evaluation output is written to:

```text
evaluation/results.md
```

## Environment Variables

Example:

```env
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
OPENROUTER_MODEL=meta-llama/llama-3.1-8b-instruct
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
VECTOR_DB_PATH=rag/vector_store
```

Current implementation uses local retrieval and deterministic workflow logic. External LLM provider variables are included for deployment extensibility.

## MCP-Style Tools

The project tools are implemented in `hr_mcp/server.py`.

Available tools include:

```text
search_policy_documents_tool
lookup_employee_profile
check_pto_balance
lookup_benefits_status
create_mock_hr_ticket
draft_hr_email
```

The tools support HR policy retrieval, employee lookup, PTO checks, benefits checks, mock HR ticket creation, and mock email drafting.

## Evaluation Summary

The evaluation set includes 24 questions/tasks covering:

- Simple policy Q&A
- Multi-document policy questions
- PTO workflows
- Remote work workflows
- Benefits workflows
- Expense workflows
- Ambiguous requests
- Out-of-scope requests
- Safety/escalation scenarios

Current evaluation metrics are recorded in:

```text
evaluation/results.md
```

The evaluation includes tool selection, citation accuracy, groundedness, workflow completion, latency, and a retrieval `top_k` comparison.

## Deployment

The application is designed for a single-service free-tier deployment. The web app, agent orchestration, RAG retriever, Chroma index, MCP-style tools, and mock data can run in one Render or Railway service.

Deployment details are documented in:

```text
deployed.md
```

## Data Notice

All employee data is synthetic and created for demonstration only. Mock HR tickets are simulated actions and do not contact any real HR system. Mock HR emails are drafted only and are not sent.

## Repository

GitHub repository:

```text
https://github.com/avermonty-ui/quantic-project-3-hr-agent
```