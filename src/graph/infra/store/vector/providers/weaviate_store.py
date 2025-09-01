from typing import Any, Dict, List, Optional

import weaviate
from weaviate.classes.config import Configure

from graph.infra.config import get_settings
from graph.infra.config.schemas.store.store_config import VectorSettings
from graph.infra.store.vector.base import BaseVectorStore
from graph.infra.store.vector.exceptions import (VectorConnectionError,
                                                 VectorDataError,
                                                 VectorIndexError,
                                                 VectorQueryError)


class WeaviateStore(BaseVectorStore):
    def __init__(
        self,
        settings: Optional[VectorSettings] = None,
        service_name: Optional[str] = "weaviate_store",
    ):
        super().__init__(service_name=service_name, provider_name="weaviate")
        self.settings = settings or get_settings().store.vector
        self.client: Optional[weaviate.WeaviateClient] = None

    async def _connect(self) -> None:
        try:
            self.client = weaviate.connect_to_local(url=self.settings.url)
        except Exception as e:
            raise VectorConnectionError("Failed to connect to Weaviate.") from e

    async def _close(self) -> None:
        if self.client:
            self.client.close()

    async def _ensure_schema_impl(self) -> None:
        try:
            doc_class = "Document"
            if doc_class not in self.client.collections.list_all():
                self.client.collections.create(
                    name=doc_class,
                    vectorizer_config=Configure.Vectorizer.none(),
                    properties=[
                        {"name": "doc_id", "dataType": "text"},
                        {"name": "text", "dataType": "text"},
                        {"name": "entities", "dataType": "text[]"},
                    ],
                )
        except Exception as e:
            raise VectorIndexError("Failed to ensure vector store schema.") from e

    async def _upsert_documents_impl(
        self, docs: List[Dict[str, Any]], vectors: Any
    ) -> None:
        try:
            col = self.client.collections.get("Document")
            with col.batch.dynamic() as batch:
                for d, v in zip(docs, vectors):
                    batch.add_object(
                        properties={
                            "doc_id": d["id"],
                            "text": d["text"],
                            "entities": d.get("entities", []),
                        },
                        vector=v,
                    )
        except Exception as e:
            raise VectorDataError(
                "Failed to upsert documents into the vector store."
            ) from e

    async def _vector_search_impl(
        self, query_vec: Any, top_k: int
    ) -> List[Dict[str, Any]]:
        try:
            col = self.client.collections.get("Document")
            res = col.query.near_vector(
                near_vector=query_vec,
                limit=top_k,
                return_metadata=["distance"],
                return_properties=["doc_id", "text", "entities"],
            )
            hits = []
            for o in res.objects:
                sim = (
                    1.0 - o.metadata.distance
                    if o.metadata.distance is not None
                    else 0.0
                )
                hits.append(
                    {
                        "doc_id": o.properties.get("doc_id"),
                        "text": o.properties.get("text", ""),
                        "entities": o.properties.get("entities", []),
                        "dense_score": float(sim),
                    }
                )
            return hits
        except Exception as e:
            raise VectorQueryError("Failed to perform vector search.") from e
