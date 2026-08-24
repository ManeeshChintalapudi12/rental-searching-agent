from agentic.ai.rag import RAGPipeline, VectorDocument


def test_rag_pipeline_handles_local_documents() -> None:
    pipeline = RAGPipeline()
    pipeline.add_documents([
        VectorDocument(id="d1", text="Danville has a strong rental market with family-friendly neighborhoods and access to Bay Area jobs.", metadata={"city": "Danville", "state": "CA"}),
        VectorDocument(id="d2", text="Seattle rents are competitive and near major employers like Amazon and Microsoft.", metadata={"city": "Seattle", "state": "WA"}),
    ])

    answer = pipeline.ask("What is the rental market like in Danville, CA?")

    assert "Danville" in answer["answer"]
    assert answer["source_ids"]
    assert answer["retrieval_count"] >= 1


def test_rag_pipeline_supports_single_document_query() -> None:
    pipeline = RAGPipeline()
    pipeline.add_documents([
        VectorDocument(id="doc-1", text="Frisco is a fast-growing suburb with strong apartment demand and low vacancy.", metadata={"city": "Frisco", "state": "TX"})
    ])

    answer = pipeline.ask("Tell me about Frisco rentals")
    assert answer["answer"]
    assert answer["source_ids"] == ["doc-1"]


def test_ai_rag_route_returns_answer() -> None:
    from app.main import app
    from fastapi.testclient import TestClient

    client = TestClient(app)
    response = client.get("/api/ai/rag", params={"question": "What is the rental market in Danville, CA?"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["question"]
    assert payload["answer"]
    assert payload["retrieval_count"] >= 1
