import time
from abc import ABC, abstractmethod
from typing import Any, Awaitable, Callable, Dict, List

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from graph.infra.observability.metrics.usage.vector_store_metrics import (
    VECTOR_STORE_LATENCY, VECTOR_STORE_OPERATIONS_TOTAL)
from graph.infra.services.base import BaseService
from graph.infra.services.protocol import BaseServiceProtocol
from graph.infra.store.vector.protocol import VectorStoreProtocol

tracer = trace.get_tracer("graph.infra.store.vector")


class BaseVectorStore(BaseService, VectorStoreProtocol, BaseServiceProtocol, ABC):
    def __init__(self, service_name: str, provider_name: str):
        super().__init__(service_name=service_name)
        self._provider_name = provider_name

    async def _instrumented_call(
        self, operation: str, func: Callable[..., Awaitable[Any]], *args, **kwargs
    ) -> Any:
        start_time = time.perf_counter()
        span_name = f"vector.store.{self._provider_name}.{operation}"

        with tracer.start_as_current_span(span_name) as span:
            span.set_attribute("vector.provider", self._provider_name)
            span.set_attribute("vector.operation", operation)

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

                VECTOR_STORE_LATENCY.labels(
                    provider=self._provider_name,
                    operation=operation,
                    status=status_label,
                ).observe(duration)
                VECTOR_STORE_OPERATIONS_TOTAL.labels(
                    provider=self._provider_name,
                    operation=operation,
                    status=status_label,
                ).inc()

    async def ensure_schema(self) -> None:
        await self._instrumented_call("ensure_schema", self._ensure_schema_impl)

    async def upsert_documents(self, docs: List[Dict[str, Any]], vectors: Any) -> None:
        await self._instrumented_call(
            "upsert_documents", self._upsert_documents_impl, docs, vectors
        )

    async def vector_search(self, query_vec: Any, top_k: int) -> List[Dict[str, Any]]:
        return await self._instrumented_call(
            "vector_search", self._vector_search_impl, query_vec, top_k
        )

    @abstractmethod
    async def _ensure_schema_impl(self) -> None:
        pass

    @abstractmethod
    async def _upsert_documents_impl(
        self, docs: List[Dict[str, Any]], vectors: Any
    ) -> None:
        pass

    @abstractmethod
    async def _vector_search_impl(
        self, query_vec: Any, top_k: int
    ) -> List[Dict[str, Any]]:
        pass
