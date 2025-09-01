# src/graph/retrieval/service.py

from typing import Any, Dict, List, Set

from loguru import logger
from sentence_transformers import SentenceTransformer

from graph.infra.observability import with_observability
from graph.infra.store.graph.protocol import GraphStoreProtocol
from graph.infra.store.vector.protocol import VectorStoreProtocol


class RetrievalService:
    """
    Orchestrates the hybrid retrieval process by combining vector search
    with graph traversal for context enrichment and re-ranking.
    """

    def __init__(
        self,
        vector_store: VectorStoreProtocol,
        graph_store: GraphStoreProtocol,
        embedding_model_name: str = "all-MiniLM-L6-v2",
        top_k: int = 10,
        graph_hops: int = 2,
        graph_limit: int = 30,
        rerank_boost: float = 0.2,
    ):
        self.logger = logger.bind(service="retrieval_service")
        self._vector_store = vector_store
        self._graph_store = graph_store
        self.embedding_model = SentenceTransformer(embedding_model_name)

        self._top_k = top_k
        self._graph_hops = graph_hops
        self._graph_limit = graph_limit
        self._rerank_boost = rerank_boost

    @with_observability(name="retrieval.hybrid_query")
    async def query(self, query_text: str) -> List[Dict[str, Any]]:
        self.logger.info(f"Received query: '{query_text}'")

        query_vector = self.embedding_model.encode(query_text).tolist()

        vector_docs = await self._vector_store.vector_search(
            query_vec=query_vector, top_k=self._top_k
        )
        self.logger.info(f"Retrieved {len(vector_docs)} documents from vector store.")

        if not vector_docs:
            return []

        seed_entities = self._extract_entities_from_docs(vector_docs)
        self.logger.info(
            f"Extracted {len(seed_entities)} seed entities for graph traversal."
        )

        if not seed_entities:
            for doc in vector_docs:
                doc["final_score"] = doc.get("dense_score", 0.0)
            return sorted(vector_docs, key=lambda d: d["final_score"], reverse=True)

        expanded_entities = await self._graph_store.expand_entities(
            start_entities=list(seed_entities),
            hops=self._graph_hops,
            limit=self._graph_limit,
        )
        self.logger.info(
            f"Expanded to {len(expanded_entities)} related entities from graph."
        )

        reranked_docs = self._fuse_and_rerank(vector_docs, expanded_entities)
        self.logger.info("Fusion and re-ranking complete.")

        return reranked_docs

    def _extract_entities_from_docs(self, docs: List[Dict[str, Any]]) -> Set[str]:
        entity_set = set()
        for doc in docs:
            entities = doc.get("entities", [])
            if entities:
                entity_set.update(entities)
        return entity_set

    def _fuse_and_rerank(
        self, vector_docs: List[Dict[str, Any]], graph_entities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        expanded_entity_ids = {entity["id"] for entity in graph_entities}
        for doc in vector_docs:
            doc_score = doc.get("dense_score", 0.0)
            boost = 0.0

            doc_entities = doc.get("entities", [])
            if doc_entities and expanded_entity_ids.intersection(doc_entities):
                boost = self._rerank_boost

            doc["final_score"] = doc_score + boost

        return sorted(
            vector_docs, key=lambda d: d.get("final_score", 0.0), reverse=True
        )
