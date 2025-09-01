# tests/retrieval/test_retrieval_service.py

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.graph.retrieval.service import RetrievalService


@pytest.fixture
def mock_vector_store():
    """Fixture for a mocked VectorStoreProtocol."""
    return AsyncMock()


@pytest.fixture
def mock_graph_store():
    """Fixture for a mocked GraphStoreProtocol."""
    return AsyncMock()


@pytest.fixture
def retrieval_service(mock_vector_store, mock_graph_store):
    """Fixture to create a RetrievalService instance with mocked dependencies."""
    service = RetrievalService(
        vector_store=mock_vector_store, graph_store=mock_graph_store, rerank_boost=0.5
    )
    service.embedding_model = MagicMock()
    service.embedding_model.encode.return_value.tolist.return_value = [0.1, 0.2, 0.3]
    return service


@pytest.mark.asyncio
async def test_query_happy_path_with_reranking(
    retrieval_service, mock_vector_store, mock_graph_store
):
    """
    Tests the full hybrid retrieval pipeline where graph expansion boosts a document's score.
    """
    # Arrange
    mock_vector_store.vector_search.return_value = [
        {
            "doc_id": "doc1",
            "text": "About apples.",
            "entities": ["apple"],
            "dense_score": 0.9,
        },
        {
            "doc_id": "doc2",
            "text": "About oranges.",
            "entities": ["orange"],
            "dense_score": 0.8,
        },
    ]
    mock_graph_store.expand_entities.return_value = [
        {"id": "apple", "label": "Fruit"},
        {"id": "tree", "label": "Plant"},
    ]

    # Act
    results = await retrieval_service.query("fruits")

    # Assert
    mock_vector_store.vector_search.assert_awaited_once()

    # --- CORREÇÃO APLICADA AQUI ---
    # We now check the call in a way that is robust to the order of the 'start_entities' list.
    mock_graph_store.expand_entities.assert_awaited_once()  # Check it was called once
    actual_call_args = mock_graph_store.expand_entities.call_args

    # Use set for order-insensitive comparison of the list
    assert set(actual_call_args.kwargs["start_entities"]) == {"apple", "orange"}
    assert actual_call_args.kwargs["hops"] == 2
    assert actual_call_args.kwargs["limit"] == 30
    # --- FIM DA CORREÇÃO ---

    assert len(results) == 2

    doc1_result = next(d for d in results if d["doc_id"] == "doc1")
    doc2_result = next(d for d in results if d["doc_id"] == "doc2")

    assert doc1_result["final_score"] == pytest.approx(1.4)
    assert doc2_result["final_score"] == pytest.approx(0.8)

    assert results[0]["doc_id"] == "doc1"
    assert results[1]["doc_id"] == "doc2"


@pytest.mark.asyncio
async def test_query_no_entities_in_vector_results(
    retrieval_service, mock_vector_store, mock_graph_store
):
    """
    Tests that graph traversal is skipped if the initial vector search returns no entities.
    """
    # Arrange
    mock_vector_store.vector_search.return_value = [
        {"doc_id": "doc3", "text": "No entities here.", "dense_score": 0.95},
        {"doc_id": "doc4", "text": "Just text.", "dense_score": 0.85},
    ]

    # Act
    results = await retrieval_service.query("some query")

    # Assert
    mock_vector_store.vector_search.assert_awaited_once()
    mock_graph_store.expand_entities.assert_not_awaited()

    assert len(results) == 2
    assert results[0]["final_score"] == pytest.approx(0.95)
    assert results[1]["final_score"] == pytest.approx(0.85)
    assert results[0]["doc_id"] == "doc3"
