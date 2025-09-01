from typing import Any, Dict, List, Protocol, runtime_checkable


@runtime_checkable
class VectorStoreProtocol(Protocol):
    """
    Protocol for a vector database, abstracting operations like ingestion and search.
    This interface ensures that the application logic remains agnostic to the underlying
    vector store implementation (e.g., Weaviate, Milvus, Pinecone).
    """

    async def ensure_schema(self) -> None:
        """
        Ensures the necessary schema/collection is created and configured.
        """
        ...

    async def upsert_documents(self, docs: List[Dict[str, Any]], vectors: Any) -> None:
        """
        Ingests documents and their corresponding vectors into the store.
        """
        ...

    async def vector_search(self, query_vec: Any, top_k: int) -> List[Dict[str, Any]]:
        """
        Performs a vector similarity search to retrieve the top-k most relevant documents.
        """
        ...
