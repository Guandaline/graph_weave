# tests/infra/store/graph/test_neo4j_integration.py

import asyncio
import uuid

import pytest

from graph.infra.config import get_settings
from graph.infra.store.graph.providers import Neo4jStoreProvider


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def neo4j_service(event_loop):
    settings = get_settings()
    service = Neo4jStoreProvider(settings.store.graph)
    await service.start()

    async with service.driver.session() as session:
        await session.run("MATCH (n) DETACH DELETE n")

    yield service

    await service.stop()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_upsert_and_expand_entities(neo4j_service: Neo4jStoreProvider):
    # Arrange: Define test data
    doc_id = f"doc_{uuid.uuid4()}"
    entity_a = {"id": "entity_A", "label": "Test", "properties": {"value": 1}}
    entity_b = {"id": "entity_B", "label": "Test", "properties": {"value": 2}}
    entity_c = {"id": "entity_C", "label": "Another", "properties": {"value": 3}}

    # Act: Ingest data
    await neo4j_service.upsert_documents([{"id": doc_id, "text": "test"}])
    await neo4j_service.upsert_entities([entity_a, entity_b, entity_c])

    await neo4j_service.link_doc_entities([(doc_id, "entity_A"), (doc_id, "entity_B")])

    async with neo4j_service.driver.session() as session:
        await session.run(
            """
            MATCH (b:Test {id: $entity_b_id}), (c:Another {id: $entity_c_id})
            MERGE (b)-[:RELATED_TO]->(c)
            """,
            entity_b_id="entity_B",
            entity_c_id="entity_C",
        )

    # Act: Expand from entity_A
    expanded_results = await neo4j_service.expand_entities(
        start_entities=["entity_A"], hops=2, limit=10
    )

    # Assert
    assert len(expanded_results) == 2

    result_ids = {e["id"] for e in expanded_results}
    assert "entity_B" in result_ids
    assert "entity_C" in result_ids
