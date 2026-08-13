from typing import Dict, List


VECTOR_DB_PATH = "rag/vector_store"
COLLECTION_NAME = "hr_policies"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


class PolicyRetriever:
    def __init__(self) -> None:
        # Lazy imports keep the FastAPI app startup lightweight on free-tier hosts.
        import chromadb
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(EMBEDDING_MODEL)
        self.client = chromadb.PersistentClient(path=VECTOR_DB_PATH)
        self.collection = self.client.get_collection(COLLECTION_NAME)

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        query_embedding = self.model.encode(
            [query],
            normalize_embeddings=True
        ).tolist()[0]

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        matches = []

        for i in range(len(results["ids"][0])):
            metadata = results["metadatas"][0][i]
            document_text = results["documents"][0][i]
            distance = results["distances"][0][i]

            matches.append(
                {
                    "id": results["ids"][0][i],
                    "score": round(1 - distance, 4),
                    "doc_id": metadata.get("doc_id"),
                    "title": metadata.get("title"),
                    "section": metadata.get("section"),
                    "source_path": metadata.get("source_path"),
                    "snippet": document_text,
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