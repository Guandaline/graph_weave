# src/graph/api/main.py

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvloop
from fastapi import FastAPI
from loguru import logger

from graph.infra.config import get_settings
from graph.infra.observability import setup_tracing
from graph.infra.store.graph.providers import Neo4jStoreProvider
from graph.infra.store.vector.providers.weaviate_store import WeaviateStore
from src.graph.retrieval.service import RetrievalService


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Manages the application's lifespan. This is the composition root where all
    services are instantiated, started, and gracefully stopped.
    """
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    logger.info("uvloop successfully installed as the event loop policy.")
    setup_tracing()
    settings = get_settings()

    # 1. Instantiate all infrastructure and application services
    neo4j_store = Neo4jStoreProvider(settings.store.graph)
    weaviate_store = WeaviateStore(settings.store.vector)

    retrieval_service = RetrievalService(
        vector_store=weaviate_store, graph_store=neo4j_store
    )

    # 2. Store instances in app.state for dependency injection
    app.state.neo4j_store = neo4j_store
    app.state.weaviate_store = weaviate_store
    app.state.retrieval_service = retrieval_service

    # 3. Start all managed services concurrently
    await asyncio.gather(neo4j_store.start(), weaviate_store.start())
    logger.info("--- Services Started Successfully ---")

    yield

    # --- Shutdown ---
    logger.info("--- Application Shutdown ---")
    await asyncio.gather(neo4j_store.stop(), weaviate_store.stop())
    logger.info("--- Services Stopped Gracefully ---")
