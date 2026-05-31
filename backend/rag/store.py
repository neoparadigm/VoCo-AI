"""
ChromaDB RAG store — in-process, local, zero-cost.
Used for semantic search over incident history.
"""

import json
import os
from typing import List


# Optional import — ChromaDB not required for MVP
try:
    import chromadb
    _CHROMA_AVAILABLE = True
except ImportError:
    _CHROMA_AVAILABLE = False


class IncidentStore:
    def __init__(self):
        self._client = None
        self._collection = None
        if _CHROMA_AVAILABLE:
            self._client = chromadb.Client()
            self._collection = self._client.get_or_create_collection("incidents")

    def ingest(self, incidents: List[dict]):
        if not _CHROMA_AVAILABLE or not incidents:
            return
        for inc in incidents:
            self._collection.upsert(
                ids=[inc["id"]],
                documents=[json.dumps(inc)],
                metadatas=[{"title": inc.get("title", ""), "severity": inc.get("severity", "")}]
            )

    def search(self, query: str, n_results: int = 3) -> List[dict]:
        if not _CHROMA_AVAILABLE or not self._collection:
            return []
        results = self._collection.query(query_texts=[query], n_results=n_results)
        return [json.loads(doc) for doc in results["documents"][0]]
