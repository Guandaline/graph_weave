# src/graph/ingestion/service.py

import asyncio
import json
from itertools import islice
from typing import Any, Dict, Generator, List

from loguru import logger
from sentence_transformers import SentenceTransformer

from graph.infra.observability.decorators import with_observability
from graph.infra.services.base import BaseService
from graph.infra.store.graph import GraphStoreProtocol
from graph.infra.store.vector import VectorStoreProtocol


class IngestionService(BaseService):
    """
    Orchestrates the data ingestion pipeline, coordinating between
    data sources and storage providers.
    """

    def __init__(
        self,
        graph_store: GraphStoreProtocol,
        vector_store: VectorStoreProtocol,
        embedding_model_name: str = "all-MiniLM-L6-v2",
        batch_size: int = 128,
    ):
        super().__init__(service_name="ingestion_service")
        self._graph_store = graph_store
        self._vector_store = vector_store
        self._batch_size = batch_size
        self.logger = logger.bind(service=self.service_name)
        # Initialize the embedding model once.
        self.embedding_model = SentenceTransformer(embedding_model_name)

    async def _connect(self) -> None:
        """
        The ingestion service itself is stateless, but it ensures its
        dependencies are ready before operating.
        """
        if not self._graph_store.is_ready() or not self._vector_store.is_ready():
            raise RuntimeError("Storage providers are not ready for ingestion.")
        self.logger.info("IngestionService is ready, dependencies are connected.")

    async def _close(self) -> None:
        self.logger.info("IngestionService is closing.")

    @with_observability(name="ingestion.run_pipeline")
    async def run_pipeline(
        self, documents_path: str, entities_path: str, edges_path: str
    ) -> None:
        """
        Executes the full ingestion pipeline: documents, entities, and their relationships.
        """
        self.logger.info("Starting data ingestion pipeline.")
        await self._ensure_schemas()

        await self._ingest_documents(documents_path)
        await self._ingest_entities(entities_path)
        await self._link_document_entities(edges_path)

        self.logger.info("Data ingestion pipeline completed successfully.")

    # --- Private Methods ---

    def _load_and_batch_data(
        self, file_path: str
    ) -> Generator[List[Dict[str, Any]], None, None]:
        """
        Loads data from a .jsonl file and yields it in batches.
        This generator approach is memory-efficient for large files.
        """
        with open(file_path, "r") as f:
            while True:
                lines_iterator = islice(f, self._batch_size)
                # The check below handles the end of the file gracefully.
                first_line = next(lines_iterator, None)
                if not first_line:
                    break

                # Reconstruct the iterator with the first line included.
                batch_lines = [first_line] + list(lines_iterator)
                batch = [json.loads(line) for line in batch_lines]
                yield batch

    async def _ensure_schemas(self) -> None:
        self.logger.info("Ensuring storage schemas and indexes are in place.")
        await asyncio.gather(
            self._graph_store.ensure_indexes(), self._vector_store.ensure_schema()
        )
        self.logger.info("Schemas and indexes are configured.")

    @with_observability(name="ingestion.ingest_documents")
    async def _ingest_documents(self, file_path: str) -> None:
        self.logger.info(f"Starting document ingestion from {file_path}...")
        total_docs = 0
        for batch in self._load_and_batch_data(file_path):
            texts = [doc["text"] for doc in batch]
            vectors = self.embedding_model.encode(texts, show_progress_bar=False)

            await asyncio.gather(
                self._vector_store.upsert_documents(docs=batch, vectors=vectors),
                self._graph_store.upsert_documents(docs=batch),
            )
            total_docs += len(batch)
            self.logger.info(f"Ingested {total_docs} documents...")
        self.logger.success(f"Finished ingesting {total_docs} documents.")

    @with_observability(name="ingestion.ingest_entities")
    async def _ingest_entities(self, file_path: str) -> None:
        self.logger.info(f"Starting entity ingestion from {file_path}...")
        total_entities = 0
        for batch in self._load_and_batch_data(file_path):
            await self._graph_store.upsert_entities(entities=batch)
            total_entities += len(batch)
            self.logger.info(f"Ingested {total_entities} entities...")
        self.logger.success(f"Finished ingesting {total_entities} entities.")

    @with_observability(name="ingestion.link_document_entities")
    async def _link_document_entities(self, file_path: str) -> None:
        self.logger.info(f"Starting to link documents and entities from {file_path}...")
        total_edges = 0
        for batch in self._load_and_batch_data(file_path):
            # The protocol expects a list of tuples: (doc_id, entity_id)
            pairs = [(edge["doc_id"], edge["entity_id"]) for edge in batch]
            await self._graph_store.link_doc_entities(pairs=pairs)
            total_edges += len(batch)
            self.logger.info(f"Linked {total_edges} relations...")
        self.logger.success(f"Finished linking {total_edges} relations.")
