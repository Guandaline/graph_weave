import time
from abc import ABC, abstractmethod
from typing import Any, Awaitable, Callable, Dict, List

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from graph.infra.observability.metrics.usage.graph_store_metrics import (
    GRAPH_STORE_LATENCY, GRAPH_STORE_OPERATIONS_TOTAL)
from graph.infra.services.base import BaseService
from graph.infra.services.protocol import BaseServiceProtocol
from graph.infra.store.graph.protocol import GraphStoreProtocol

tracer = trace.get_tracer("graph.infra.store.graph")


class BaseGraphStore(BaseService, GraphStoreProtocol, BaseServiceProtocol, ABC):
    """
    Abstract base class for all graph store providers. It centralizes lifecycle management,
    metrics, and tracing for all graph operations.
    """

    def __init__(self, service_name: str, provider_name: str):
        super().__init__(service_name=service_name)
        self._provider_name = provider_name

    async def _instrumented_call(
        self, operation: str, func: Callable[..., Awaitable[Any]], *args, **kwargs
    ) -> Any:
        start_time = time.perf_counter()
        span_name = f"graph.store.{self._provider_name}.{operation}"

        with tracer.start_as_current_span(span_name) as span:
            span.set_attribute("graph.provider", self._provider_name)
            span.set_attribute("graph.operation", operation)

            status_label = "failure"
            try:
                result = await func(*args, **kwargs)
                status_label = "success"
                span.set_status(Status(StatusCode.OK))
                return result
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise
            finally:
                duration = time.perf_counter() - start_time

                GRAPH_STORE_LATENCY.labels(
                    provider=self._provider_name,
                    operation=operation,
                    status=status_label,
                ).observe(duration)
                GRAPH_STORE_OPERATIONS_TOTAL.labels(
                    provider=self._provider_name,
                    operation=operation,
                    status=status_label,
                ).inc()

    async def ensure_indexes(self) -> None:
        await self._instrumented_call("ensure_indexes", self._ensure_indexes_impl)

    async def upsert_entities(self, entities: List[Dict[str, Any]]) -> None:
        await self._instrumented_call(
            "upsert_entities", self._upsert_entities_impl, entities
        )

    async def upsert_documents(self, docs: List[Dict[str, Any]]) -> None:
        await self._instrumented_call(
            "upsert_documents", self._upsert_documents_impl, docs
        )

    async def link_doc_entities(self, pairs: List[tuple[str, str]]) -> None:
        await self._instrumented_call(
            "link_doc_entities", self._link_doc_entities_impl, pairs
        )

    async def expand_entities(
        self, start_entities: List[str], hops: int, limit: int
    ) -> List[Dict[str, Any]]:
        return await self._instrumented_call(
            "expand_entities", self._expand_entities_impl, start_entities, hops, limit
        )

    @abstractmethod
    async def _ensure_indexes_impl(self) -> None:
        pass

    @abstractmethod
    async def _upsert_entities_impl(self, entities: List[Dict[str, Any]]) -> None:
        pass

    @abstractmethod
    async def _upsert_documents_impl(self, docs: List[Dict[str, Any]]) -> None:
        pass

    @abstractmethod
    async def _link_doc_entities_impl(self, pairs: List[tuple[str, str]]) -> None:
        pass

    @abstractmethod
    async def _expand_entities_impl(
        self, start_entities: List[str], hops: int, limit: int
    ) -> List[Dict[str, Any]]:
        pass
