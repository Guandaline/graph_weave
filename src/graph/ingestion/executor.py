import asyncio

from graph.infra.config import get_settings
from graph.infra.store.graph.providers import Neo4jStoreProvider
from graph.infra.store.vector.providers.weaviate_store import WeaviateStore

from .service import IngestionService


async def main():
    """
    Initializes the application components and runs the ingestion service.
    """
    settings = get_settings()

    # 1. Instantiate concrete dependencies
    neo4j_provider = Neo4jStoreProvider(settings.store.graph)
    weaviate_provider = WeaviateStore(settings.store.vector)

    # 2. Instantiate the orchestrator service, injecting dependencies
    ingestion_service = IngestionService(
        graph_store=neo4j_provider, vector_store=weaviate_provider
    )

    # Use a try/finally block to ensure graceful shutdown
    try:
        # 3. Start all services
        # The IngestionService will check the readiness of its dependencies.
        await asyncio.gather(
            neo4j_provider.start(), weaviate_provider.start(), ingestion_service.start()
        )

        # 4. Execute the pipeline
        await ingestion_service.run_pipeline(
            documents_path="data/documents.jsonl",
            entities_path="data/entities.jsonl",
            edges_path="data/edges.jsonl",
        )

    except Exception:
        logger.exception("An error occurred during the ingestion process.")
    finally:
        # 5. Stop all services gracefully
        await asyncio.gather(
            ingestion_service.stop(), weaviate_provider.stop(), neo4j_provider.stop()
        )


if __name__ == "__main__":
    # Setup observability (tracing, etc.) before running anything
    from loguru import logger

    from graph.infra.observability import setup_tracing

    setup_tracing()

    logger.info("Starting ingestion process...")
    asyncio.run(main())
    logger.info("Ingestion process finished.")
