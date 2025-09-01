from typing import Any


class VectorStoreError(Exception):
    """Base exception for all errors in the vector store provider."""

    pass


class VectorConnectionError(VectorStoreError):
    """Raised when there is an issue establishing or maintaining a connection to the vector database."""

    pass


class VectorQueryError(VectorStoreError):
    """Raised when a vector search query fails to execute correctly."""

    def __init__(self, message: str, query_vec: Any = None):
        super().__init__(message)
        self.query_vec = query_vec


class VectorIndexError(VectorStoreError):
    """Raised when there is an issue with creating or verifying a vector index."""

    pass


class VectorDataError(VectorStoreError):
    """Raised for issues related to data integrity within the vector store."""

    pass
