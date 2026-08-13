# Deployment

## Deployment Status

The Northstar PeopleOps Assistant has been deployed successfully on Render as a free-tier Web Service.

Deployment platform:

```text
Render
```

Deployment type:

```text
Web Service
```

Runtime:

```text
Python 3
```

## Deployed URLs

Application URL:

```text
https://quantic-project-3-hr-agent.onrender.com/
```

Health endpoint:

```text
https://quantic-project-3-hr-agent.onrender.com/health
```

API docs:

```text
https://quantic-project-3-hr-agent.onrender.com/docs
```

OpenAPI schema:

```text
https://quantic-project-3-hr-agent.onrender.com/openapi.json
```

## Verified Deployment Checks

The following deployed checks were completed successfully:

- The homepage loads at `/`.
- The health endpoint returns status `ok`.
- The Swagger/OpenAPI docs load at `/docs`.
- Demo 1, PTO request guidance, works on the deployed app.
- Demo 2, extended remote work review, works on the deployed app.
- The deployed app returns answers, citations, snippets, and an operational tool trace.

## Health Endpoint Response

The deployed health endpoint returns:

```json
{
  "status": "ok",
  "app": "quantic-project-3-hr-agent",
  "mcp_tools": "available",
  "rag_index": "available"
}
```

## Render Configuration

Build command:

```bash
pip install -r requirements.txt && python rag/ingest.py
```

Start command:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 10000
```

Render environment variable:

```text
PORT=10000
```

Additional environment variables:

```env
LLM_PROVIDER=groq
GROQ_MODEL=llama-3.1-8b-instant
OPENROUTER_MODEL=meta-llama/llama-3.1-8b-instruct
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
VECTOR_DB_PATH=rag/vector_store
PYTHON_VERSION=3.11.9
```

Real API keys are not required for the current deterministic demo workflows and are not committed to the repository.

## Deployment Architecture

The app is deployed as a single Render Web Service.

```text
Render Web Service
  |
  |-- FastAPI application
  |-- Branded web chat UI
  |-- Agent orchestrator
  |-- Policy retriever
  |-- MCP-style HR tools
  |-- Mock JSON HR data
  |-- Markdown policy corpus
```

This single-service deployment keeps the project compatible with free-tier hosting.

## Free-Tier Runtime Adjustment

The original RAG ingestion pipeline builds a Chroma vector index with `sentence-transformers`. This still runs during the Render build step.

However, Render Free has limited memory. Loading `sentence-transformers` and `torch` during live chat requests caused the deployed `/chat` workflow to hang. To keep the deployed demo reliable on the free tier, the runtime retriever was changed to a lightweight section-based keyword retriever.

The project still includes:

- `rag/ingest.py`
- ChromaDB indexing
- `sentence-transformers` embedding pipeline
- local vector store generation
- RAG design documentation
- evaluation results

The deployed app uses the lightweight runtime retriever for free-tier compatibility while preserving cited policy retrieval behavior.

## Demo 1: PTO Request Guidance

Live prompt:

```text
Can Avery Kim take three days of PTO next week?
```

Expected deployed behavior:

1. Looks up Avery Kim's employee profile.
2. Checks Avery Kim's PTO balance.
3. Retrieves PTO policy citations.
4. Drafts a mock manager email.
5. Returns a final answer with citations and tool trace.

## Demo 2: Extended Remote Work Review

Live prompt:

```text
Can Maya Patel work remotely from another state for six weeks?
```

Expected deployed behavior:

1. Looks up Maya Patel's employee profile.
2. Retrieves remote work policy citations.
3. Determines that manager and HR approval are required.
4. Creates a mock HR ticket.
5. Returns a final answer with citations and tool trace.

## Cold Start Notes

Render free-tier services may spin down after inactivity. The first request after a period of inactivity may take 50 seconds or more.

After startup, normal page loads and workflow responses are faster.