from typing import Any, Dict, List, Optional, Tuple

import neo4j
from neo4j.exceptions import ServiceUnavailable

from graph.infra.config import get_settings
from graph.infra.config.schemas.store.store_config import GraphSettings

from ..base import BaseGraphStore
from ..exceptions import (GraphConnectionError, GraphDataError,
                          GraphIndexError, GraphQueryError)


class Neo4jStoreProvider(BaseGraphStore):
    def __init__(
        self,
        settings: Optional[GraphSettings] = None,
        service_name: str = "neo4j_store",
    ):
        super().__init__(service_name=service_name, provider_name="neo4j")
        self.settings = settings or get_settings().store.graph
        self.driver: Optional[neo4j.AsyncDriver] = None

    async def _connect(self) -> None:
        try:
            self.driver = neo4j.AsyncGraphDatabase.driver(
                self.settings.uri,
                auth=(self.settings.user, self.settings.password),
            )
            await self.driver.verify_connectivity()
        except ServiceUnavailable as e:
            raise GraphConnectionError("Failed to connect to Neo4j.") from e
        except Exception as e:
            raise GraphConnectionError(
                "An unexpected error occurred during connection."
            ) from e

    async def _close(self) -> None:
        if self.driver:
            await self.driver.close()

    async def _ensure_indexes_impl(self) -> None:
        try:
            async with self.driver.session() as session:
                await session.run(
                    "CREATE CONSTRAINT ON (e:Entity) ASSERT e.id IS UNIQUE"
                )
                await session.run(
                    "CREATE CONSTRAINT ON (d:Document) ASSERT d.id IS UNIQUE"
                )
                await session.run("CREATE INDEX ON :Entity(name)")
        except Exception as e:
            raise GraphIndexError("Failed to ensure graph indexes.") from e

    async def _upsert_entities_impl(self, entities: List[Dict[str, Any]]) -> None:
        try:
            async with self.driver.session() as session:
                await session.run(
                    """
                    UNWIND $rows AS row
                    MERGE (e:Entity {id: row.id})
                    ON CREATE SET e.name = row.name
                    ON MATCH SET e.name = row.name
                    """,
                    rows=entities,
                )
        except Exception as e:
            raise GraphDataError("Failed to upsert entities.") from e

    async def _upsert_documents_impl(self, docs: List[Dict[str, Any]]) -> None:
        try:
            async with self.driver.session() as session:
                await session.run(
                    """
                    UNWIND $rows AS row
                    MERGE (d:Document {id: row.id})
                    ON CREATE SET d.length = row.length
                    """,
                    rows=[{"id": d["id"], "length": len(d["text"])} for d in docs],
                )
        except Exception as e:
            raise GraphDataError("Failed to upsert document nodes.") from e

    async def _link_doc_entities_impl(self, pairs: List[Tuple[str, str]]) -> None:
        try:
            async with self.driver.session() as session:
                await session.run(
                    """
                    UNWIND $rows AS row
                    MATCH (d:Document {id: row[0]}), (e:Entity {id: row[1]})
                    MERGE (d)-[:MENTIONS]->(e)
                    """,
                    rows=pairs,
                )
        except Exception as e:
            raise GraphDataError("Failed to link documents and entities.") from e

    async def _expand_entities_impl(
        self, start_entities: List[str], hops: int, limit: int
    ) -> List[Dict[str, Any]]:
        try:
            query = f"""
            MATCH (e:Entity)
            WHERE e.id IN $start_entities
            MATCH (e)-[:RELATED*1..{hops}]->(x:Entity)
            WITH DISTINCT x LIMIT $limit
            RETURN x.id AS id, x.name AS name
            """
            async with self.driver.session() as session:
                result = await session.run(
                    query, start_entities=start_entities, limit=limit
                )
                return [record.data() async for record in result]
        except Exception as e:
            raise GraphQueryError(
                "Failed to expand entities with the given query."
            ) from e
