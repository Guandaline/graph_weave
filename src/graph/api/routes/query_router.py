# src/graph/api/routes/query_router.py

from typing import List

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from src.graph.retrieval.service import RetrievalService

# --- Pydantic Models for API Contract ---


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=3, description="The user query to search for.")


class Citation(BaseModel):
    doc_id: str
    text: str
    final_score: float


class QueryResponse(BaseModel):
    context: str
    citations: List[Citation]


# --- Dependency ---


def get_retrieval_service(request: Request) -> RetrievalService:
    """FastAPI dependency to get the RetrievalService instance from app state."""
    return request.app.state.retrieval_service


# --- Router Definition ---

router = APIRouter(prefix="/query", tags=["Retrieval"])


@router.post("", response_model=QueryResponse)
async def query_endpoint(
    request: QueryRequest,
    retrieval_service: RetrievalService = Depends(get_retrieval_service),
):
    """
    Receives a query, performs hybrid retrieval, and returns the
    synthesized context along with citations.
    """
    retrieved_docs = await retrieval_service.query(request.query)

    citations = [
        Citation(
            doc_id=doc.get("doc_id", ""),
            text=doc.get("text", ""),
            final_score=doc.get("final_score", 0.0),
        )
        for doc in retrieved_docs
    ]

    # In a real system, this context would be fed to an LLM.
    context = " ".join([doc.get("text", "") for doc in retrieved_docs[:3]])

    return QueryResponse(context=context, citations=citations)
