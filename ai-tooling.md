# AI Tooling

## Overview

AI tools were used to accelerate development of the Northstar PeopleOps Assistant for Quantic Project 3. The project owner remained responsible for reviewing, testing, debugging, and validating the final implementation.

The application includes a FastAPI web app, RAG pipeline, Chroma vector store, MCP-style HR tools, synthetic HR data, automated tests, GitHub Actions CI, and evaluation scripts.

## AI Tools Used

AI assistance was used for:

- Planning the project architecture
- Creating the initial repository structure
- Drafting synthetic HR policy documents
- Drafting synthetic mock HR data
- Designing the RAG ingestion and retrieval pipeline
- Creating FastAPI endpoint structure
- Implementing MCP-style tool functions
- Debugging Python import and indentation issues
- Creating pytest tests
- Creating GitHub Actions CI configuration
- Drafting evaluation questions and metrics
- Drafting project documentation

## How AI Helped

AI tooling was most useful for quickly generating starter code and documentation structure. It also helped identify the implementation order used in this project:

1. Git and GitHub setup
2. Mock HR data
3. HR policy documents
4. RAG ingestion
5. RAG retrieval
6. MCP-style tools
7. FastAPI endpoints
8. Branded chat UI
9. Tests
10. GitHub Actions CI
11. Evaluation
12. Documentation

AI assistance also helped troubleshoot several implementation issues:

- Avoiding accidental API key exposure in Git history
- Cleaning local Git history before pushing to GitHub
- Resolving a Python import conflict between the local `mcp/` folder and the installed `mcp` package
- Renaming the local MCP implementation folder to `hr_mcp/`
- Adding `pytest.ini` so pytest could import project modules correctly
- Fixing Python indentation errors in `app/agent.py`
- Improving intent routing so expense questions did not incorrectly route to remote work workflows
- Improving the homepage user experience and branding

## Human Review and Manual Changes

All generated code and documentation were reviewed before being committed. The project owner manually tested the application locally using:

```bash
pytest
uvicorn app.main:app --reload
python rag/ingest.py
python -m evaluation.run_eval
```

The project owner also reviewed the application in the browser through:

```text
http://127.0.0.1:8000/
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/health
```

Several changes were made after manual review, including:

- Improving the homepage visual design
- Rebranding the interface as Northstar PeopleOps Assistant
- Supporting employee lookup by either employee ID or employee name
- Tightening expense workflow retrieval so home office chair questions cite the expense policy instead of the remote work policy
- Adding an evaluation set with 24 questions and tasks
- Adding a retrieval `top_k` ablation summary
- Adding tests for health, chat, employee lookup, PTO lookup, benefits lookup, and policy search

## What Worked Well

AI assistance worked well for:

- Structuring the project
- Drafting repeatable setup commands
- Creating initial Python modules
- Writing testable functions
- Generating documentation drafts
- Explaining Git, GitHub, and GitHub Actions steps
- Creating realistic but synthetic HR policies and employee data
- Debugging errors from terminal screenshots
- Improving the application user interface for the demo

## What Did Not Work Perfectly

AI-generated code still required review and debugging. Specific issues included:

- Some generated instructions initially used a local folder named `mcp/`, which conflicted with the installed `mcp` Python package.
- Some pasted Python blocks introduced indentation errors that had to be corrected manually.
- Initial routing logic sent an expense question containing the word “remote” to the remote work workflow instead of the expense workflow.
- Evaluation scoring is heuristic and still benefits from manual review.
- The deterministic agent workflow is effective for the project demo, but it is not a fully autonomous planning loop.

## Academic Integrity and Responsibility

AI tools were used as development aids, not as a replacement for project understanding or validation. The project owner reviewed, tested, corrected, and committed the final code and documentation.

All mock employee data is synthetic. No private company data or real employee data is included.

## Security Notes

Real API keys were not committed to the final GitHub repository. API keys are intended to be stored only in a local `.env` file or deployment environment variables.

The committed `.env.example` file contains placeholder values only.

## Final Notes

AI tooling helped accelerate implementation, but the final project was manually reviewed and tested through local execution, pytest, GitHub Actions CI, browser testing, and the evaluation runner.