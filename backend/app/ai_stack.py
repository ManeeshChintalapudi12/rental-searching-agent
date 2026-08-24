from agentic.ai.langgraph.agent import LangGraphRentalAgent
from agentic.ai.rag import BedrockEmbeddingAdapter, OpenAIEmbeddingAdapter, RAGPipeline, VectorDBAdapter, VectorDocument


class RentalAIStack:
    def __init__(self) -> None:
        self.vector_db = VectorDBAdapter()
        self.rag = RAGPipeline(self.vector_db.store)
        self.langgraph = LangGraphRentalAgent()
        self.openai_embeddings = OpenAIEmbeddingAdapter()
        self.bedrock_embeddings = BedrockEmbeddingAdapter()

    def ingest(self, documents: list[VectorDocument] | list[dict[str, object]]) -> None:
        normalized = []
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
        self.vector_db.add_documents(normalized)

    def query(self, question: str) -> dict[str, object]:
        response = self.rag.ask(question)
        return {
            "question": question,
            "answer": response["answer"],
            "source_ids": response["source_ids"],
            "retrieval_count": response["retrieval_count"],
            "langgraph": self.langgraph.run(question, response["context"].split("\n\n")),
        }
