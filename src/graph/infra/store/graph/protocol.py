from typing import Any, Dict, List, Protocol, runtime_checkable


@runtime_checkable
class GraphStoreProtocol(Protocol):
    """
    Protocol for a graph database, abstracting entity and relationship management.
    This interface decouples the application from the specific graph database vendor (e.g., Neo4j).
    """

    async def ensure_indexes(self) -> None:
        """
        Ensures all necessary indexes and constraints are in place for the graph schema.
        """
        ...

    async def upsert_entities(self, entities: List[Dict[str, Any]]) -> None:
        """
        Creates or updates a batch of entities (nodes) in the graph.
        """
        ...

    async def upsert_documents(self, docs: List[Dict[str, Any]]) -> None:
        """
        Creates or updates nodes representing documents in the graph.
        """
        ...

    async def link_doc_entities(self, pairs: List[tuple[str, str]]) -> None:
        """
        Creates relationships between documents and entities.
        """
        ...

    async def expand_entities(
        self, start_entities: List[str], hops: int, limit: int
    ) -> List[Dict[str, Any]]:
        """
        Traverses the graph to find related entities starting from a set of seed entities.
        """
        ...
