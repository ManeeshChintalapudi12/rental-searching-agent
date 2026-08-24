from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any


@dataclass
class VectorDocument:
    id: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


class SimpleVectorStore:
    def __init__(self) -> None:
        self._docs: list[VectorDocument] = []

    def add_documents(self, documents: list[VectorDocument] | list[dict[str, Any]]) -> None:
        normalized: list[VectorDocument] = []
        for document in documents:
            if isinstance(document, dict):
                normalized.append(
                    VectorDocument(
                        id=str(document.get("id", "doc")),
                        text=str(document.get("text", "")),
                        metadata=dict(document.get("metadata", {}) or {}),
                    )
                )
            else:
                normalized.append(document)
        self._docs.extend(normalized)

    def similarity_search(self, query: str, k: int = 3) -> list[VectorDocument]:
        query_lower = query.lower()
        scored = []
        for doc in self._docs:
            score = 0
            for word in query_lower.split():
                if word and word in doc.text.lower():
                    score += 1
            scored.append((score, doc))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [doc for _, doc in scored[:k] if _ > 0] or self._docs[:k]


class RAGPipeline:
    def __init__(self, vector_store: SimpleVectorStore | None = None) -> None:
        self.vector_store = vector_store or SimpleVectorStore()

    def add_documents(self, documents: list[VectorDocument] | list[dict[str, Any]]) -> None:
        self.vector_store.add_documents(documents)

    def ask(self, question: str) -> dict[str, Any]:
        matches = self.vector_store.similarity_search(question, k=3)
        context = "\n\n".join(f"[{doc.id}] {doc.text}" for doc in matches)
        answer = (
            f"Based on the retrieved market context:\n\n{context}\n\n"
            f"Answer: {question} The strongest relevant evidence points to the most similar local market data in the retrieved documents."
        )

        return {
            "answer": answer,
            "source_ids": [doc.id for doc in matches],
            "retrieval_count": len(matches),
            "context": context,
        }


class OpenAIEmbeddingAdapter:
    def __init__(self, api_key: str | None = None, model: str = "text-embedding-3-small") -> None:
        self.api_key = api_key
        self.model = model

    def embed_text(self, text: str) -> list[float]:
        if not text:
            return []
        return [float(len(text)), float(sum(ord(ch) for ch in text) % 1000) / 1000.0]


class BedrockEmbeddingAdapter:
    def __init__(self, model_id: str = "amazon.titan-embed-text-v2:0") -> None:
        self.model_id = model_id

    def embed_text(self, text: str) -> list[float]:
        if not text:
            return []
        return [float(len(text)) / 10.0, float(sum(ord(ch) for ch in text) % 1000) / 1000.0]


class VectorDBAdapter:
    def __init__(self) -> None:
        self.store = SimpleVectorStore()

    def add_documents(self, documents: list[VectorDocument]) -> None:
        self.store.add_documents(documents)

    def search(self, query: str, k: int = 3) -> list[VectorDocument]:
        return self.store.similarity_search(query, k)


def build_rag_from_documents(documents: list[VectorDocument]) -> RAGPipeline:
    pipeline = RAGPipeline()
    pipeline.add_documents(documents)
    return pipeline


def serialize_vector_documents(documents: list[VectorDocument]) -> str:
    return json.dumps([{"id": doc.id, "text": doc.text, "metadata": doc.metadata} for doc in documents])
