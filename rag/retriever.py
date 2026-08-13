from pathlib import Path
from typing import Dict, List
import re


POLICY_DIR = Path("policies")


def tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-zA-Z][a-zA-Z0-9_-]*", text.lower()))


def extract_title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line.replace("# ", "").strip()
    return fallback.replace("_", " ").title()


def section_chunks(path: Path) -> List[Dict]:
    text = path.read_text(encoding="utf-8")
    title = extract_title(text, path.stem)
    sections = re.split(r"(?=^## )", text, flags=re.MULTILINE)

    chunks = []

    for section in sections:
        section = section.strip()
        if not section:
            continue

        first_line = section.splitlines()[0].strip()
        if first_line.startswith("## "):
            section_title = first_line.replace("## ", "").strip()
        elif first_line.startswith("# "):
            section_title = first_line.replace("# ", "").strip()
        else:
            section_title = "Overview"

        chunks.append(
            {
                "doc_id": path.stem,
                "title": title,
                "section": section_title,
                "source_path": str(path),
                "snippet": section,
            }
        )

    return chunks


class PolicyRetriever:
    def __init__(self) -> None:
        self.chunks: List[Dict] = []

        for path in sorted(POLICY_DIR.glob("*.md")):
            self.chunks.extend(section_chunks(path))

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        query_terms = tokenize(query)
        scored = []

        for chunk in self.chunks:
            searchable_text = " ".join(
                [
                    chunk["title"],
                    chunk["section"],
                    chunk["snippet"],
                ]
            )
            chunk_terms = tokenize(searchable_text)

            overlap = query_terms.intersection(chunk_terms)
            score = len(overlap)

            # Small boosts for exact phrase relevance.
            lower_query = query.lower()
            lower_text = searchable_text.lower()

            if "home office" in lower_query and "home office" in lower_text:
                score += 4
            if "pto" in lower_query and "pto" in lower_text:
                score += 4
            if "remote" in lower_query and "remote" in lower_text:
                score += 3
            if "benefits" in lower_query and "benefits" in lower_text:
                score += 3
            if "expense" in lower_query and "expense" in lower_text:
                score += 4
            if "chair" in lower_query and "chair" in lower_text:
                score += 4
            if "password" in lower_query and "password" in lower_text:
                score += 4
            if "phishing" in lower_query and "phishing" in lower_text:
                score += 4

            if score > 0:
                scored.append((score, chunk))

        scored.sort(key=lambda item: item[0], reverse=True)

        matches = []
        max_score = scored[0][0] if scored else 1

        for index, (score, chunk) in enumerate(scored[:top_k]):
            matches.append(
                {
                    "id": f"{chunk['doc_id']}-{index}",
                    "score": round(score / max_score, 4),
                    "doc_id": chunk["doc_id"],
                    "title": chunk["title"],
                    "section": chunk["section"],
                    "source_path": chunk["source_path"],
                    "snippet": chunk["snippet"],
                }
            )

        return matches


_RETRIEVER = None


def get_retriever() -> PolicyRetriever:
    global _RETRIEVER

    if _RETRIEVER is None:
        _RETRIEVER = PolicyRetriever()

    return _RETRIEVER


def search_policy_documents(query: str, top_k: int = 5) -> List[Dict]:
    retriever = get_retriever()
    return retriever.search(query=query, top_k=top_k)


if __name__ == "__main__":
    retriever = get_retriever()

    test_queries = [
        "Can an employee take three days of PTO next week?",
        "Can an employee work remotely from another state for six weeks?",
        "Can a remote employee expense a home office chair?",
    ]

    for query in test_queries:
        print("\n" + "=" * 80)
        print(f"Query: {query}")
        print("=" * 80)

        matches = retriever.search(query, top_k=3)

        for match in matches:
            print(f"\nSource: {match['title']} / {match['section']}")
            print(f"Score: {match['score']}")
            print(match["snippet"][:500])