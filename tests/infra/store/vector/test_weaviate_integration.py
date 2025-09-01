# tests/infra/store/vector/test_weaviate_integration.py

import asyncio
import uuid

import pytest
from sentence_transformers import SentenceTransformer

from graph.infra.config import get_settings
from graph.infra.store.vector.providers.weaviate_store import WeaviateStore


@pytest.fixture(scope="module")
async def weaviate_service():
    """
    Provides a connected WeaviateStore service for integration tests.
    It creates a temporary schema for the test and ensures it is deleted afterwards.
    """
    settings = get_settings()
    # Modify class name for test isolation to avoid conflicts
    test_class_name = f"TestDocument_{uuid.uuid4().hex}"
    settings.store.vector.class_name = test_class_name

    service = WeaviateStore(settings.store.vector)
    await service.start()

    yield service

    # Teardown: Clean up the test schema from Weaviate and close connection
    try:
        if service._client.schema.exists(test_class_name):
            service._client.schema.delete_class(test_class_name)
    finally:
        await service.stop()


@pytest.fixture(scope="module")
def embedding_model():
    """Provides a SentenceTransformer model for generating embeddings."""
    return SentenceTransformer("all-MiniLM-L6-v2")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_upsert_and_vector_search(
    weaviate_service: WeaviateStore, embedding_model
):
    """
    Tests the full cycle of schema creation, document upsert, and vector search.
    """
    # Arrange: Define test documents and a query
    docs_to_ingest = [
        {
            "doc_id": "tech-001",
            "text": "Self-driving cars are powered by AI and machine learning.",
            "entities": ["AI"],
        },
        {
            "doc_id": "health-001",
            "text": "A balanced diet and regular exercise are key to a healthy lifestyle.",
            "entities": ["diet"],
        },
    ]

    # Generate vectors for the documents
    texts = [doc["text"] for doc in docs_to_ingest]
    vectors = embedding_model.encode(texts).tolist()

    query_text = "What is the future of artificial intelligence in vehicles?"
    query_vector = embedding_model.encode(query_text).tolist()

    # Act: Ensure schema, upsert data, and perform a search
    await weaviate_service.ensure_schema()
    await weaviate_service.upsert_documents(docs=docs_to_ingest, vectors=vectors)

    # Give Weaviate a moment to index the new objects
    await asyncio.sleep(1)

    search_results = await weaviate_service.vector_search(
        query_vec=query_vector, top_k=1
    )

    # Assert: Verify the search results
    assert len(search_results) == 1

    top_result = search_results[0]

    # The query is about AI and vehicles, so "tech-001" should be the top result.
    assert top_result["doc_id"] == "tech-001"
    assert "dense_score" in top_result
    assert top_result["dense_score"] > 0  # Should have some similarity score
    assert (
        top_result["text"]
        == "Self-driving cars are powered by AI and machine learning."
    )
