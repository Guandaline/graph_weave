class GraphStoreError(Exception):
    """Base exception for all errors in the graph store provider."""

    pass


class GraphConnectionError(GraphStoreError):
    """Raised when there is an issue establishing or maintaining a connection to the graph database."""

    pass


class GraphQueryError(GraphStoreError):
    """Raised when a graph query fails to execute correctly."""

    def __init__(self, message: str, query: str = None):
        super().__init__(message)
        self.query = query


class GraphIndexError(GraphStoreError):
    """Raised when there is an issue with creating or verifying a graph index."""

    pass


class GraphDataError(GraphStoreError):
    """Raised for issues related to data integrity within the graph store (e.g., malformed data during upsert)."""

    pass
