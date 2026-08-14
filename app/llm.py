import os
from typing import Any, Dict, List

import httpx


GROQ_CHAT_COMPLETIONS_URL = "https://api.groq.com/openai/v1/chat/completions"


def generate_final_answer(
    user_message: str,
    draft_answer: str,
    citations: List[Dict[str, Any]],
    snippets: List[Dict[str, Any]],
    tool_trace: List[Dict[str, Any]],
) -> str:
    provider = os.getenv("LLM_PROVIDER", "groq").lower()

    if provider != "groq":
        return draft_answer

    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

    if not api_key:
        return draft_answer

    system_prompt = """
You are Northstar PeopleOps Assistant, an HR policy and operations assistant.

Use only the provided policy snippets and tool outputs.
Do not invent employee data, policy rules, approvals, benefits, balances, or actions.
If the policy evidence is insufficient, say what is missing.
Mention that mock tickets and mock emails are simulated only when relevant.
Write a concise final answer for the employee or HR user.
Do not expose hidden reasoning.
""".strip()

    user_prompt = {
        "user_message": user_message,
        "draft_answer_from_workflow": draft_answer,
        "citations": citations,
        "policy_snippets": [
            {
                "title": snippet.get("title"),
                "section": snippet.get("section"),
                "source_path": snippet.get("source_path"),
                "snippet": snippet.get("snippet"),
            }
            for snippet in snippets
        ],
        "tool_trace_summary": [
            {
                "tool": step.get("tool"),
                "arguments": step.get("arguments"),
                "output": step.get("output"),
            }
            for step in tool_trace
        ],
    }

    try:
        response = httpx.post(
            GROQ_CHAT_COMPLETIONS_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": str(user_prompt)},
                ],
                "temperature": 0.2,
                "max_tokens": 700,
            },
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()
        answer = data["choices"][0]["message"]["content"].strip()

        if answer:
            return answer

    except Exception as exc:
        print(f"LLM generation failed; using draft answer. Error: {exc}")

    return draft_answer