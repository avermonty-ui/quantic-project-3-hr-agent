from pathlib import Path
from typing import List, Dict
import re
import chromadb
from sentence_transformers import SentenceTransformer


POLICY_DIR = Path("policies")
VECTOR_DB_PATH = "rag/vector_store"
COLLECTION_NAME = "hr_policies"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def read_markdown_files(policy_dir: Path) -> List[Dict]:
    documents = []

    for path in sorted(policy_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        title = extract_title(text) or path.stem.replace("_", " ").title()

        documents.append(
            {
                "doc_id": path.stem,
                "title": title,
                "source_path": str(path),
                "text": text,
            }
        )

    return documents


def extract_title(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line.replace("# ", "").strip()
    return ""


def chunk_markdown_document(document: Dict, max_chars: int = 1200, overlap: int = 150) -> List[Dict]:
    text = document["text"]

    sections = re.split(r"(?=^## )", text, flags=re.MULTILINE)
    chunks = []

    for section in sections:
        section = section.strip()
        if not section:
            continue

        section_title = "Overview"
        first_line = section.splitlines()[0].strip()
        if first_line.startswith("## "):
            section_title = first_line.replace("## ", "").strip()
        elif first_line.startswith("# "):
            section_title = first_line.replace("# ", "").strip()

        if len(section) <= max_chars:
            chunks.append(make_chunk(document, section_title, section))
        else:
            start = 0
            while start < len(section):
                end = start + max_chars
                chunk_text = section[start:end].strip()
                chunks.append(make_chunk(document, section_title, chunk_text))
                start = end - overlap

    return chunks


def make_chunk(document: Dict, section_title: str, chunk_text: str) -> Dict:
    return {
        "doc_id": document["doc_id"],
        "title": document["title"],
        "section": section_title,
        "source_path": document["source_path"],
        "text": chunk_text,
    }


def build_index() -> None:
    documents = read_markdown_files(POLICY_DIR)

    if not documents:
        raise RuntimeError(f"No markdown files found in {POLICY_DIR}")

    chunks = []
    for document in documents:
        chunks.extend(chunk_markdown_document(document))

    print(f"Loaded {len(documents)} policy documents")
    print(f"Created {len(chunks)} chunks")

    model = SentenceTransformer(EMBEDDING_MODEL)
    texts = [chunk["text"] for chunk in chunks]
    embeddings = model.encode(texts, normalize_embeddings=True).tolist()

    client = chromadb.PersistentClient(path=VECTOR_DB_PATH)

    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = client.create_collection(name=COLLECTION_NAME)

    ids = [f"{chunk['doc_id']}-{i}" for i, chunk in enumerate(chunks)]

    metadatas = [
        {
            "doc_id": chunk["doc_id"],
            "title": chunk["title"],
            "section": chunk["section"],
            "source_path": chunk["source_path"],
        }
        for chunk in chunks
    ]

    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    print(f"Saved Chroma index to {VECTOR_DB_PATH}")
    print(f"Collection name: {COLLECTION_NAME}")


if __name__ == "__main__":
    build_index()