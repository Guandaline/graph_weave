import functools
import inspect
from typing import Any, Callable, Optional

from opentelemetry.trace import SpanKind

from graph.infra.context.context_vars import get_request_id, get_trace_id
from graph.infra.observability.tracing.tracing import get_tracer


def with_span(
    name: Optional[str] = None,
    kind: SpanKind = SpanKind.INTERNAL,
    attributes_from_args: Optional[dict[str, str]] = None,
    static_attributes: Optional[dict[str, Any]] = None,
) -> Callable[..., Any]:
    """
    Cria um span OpenTelemetry ao redor da função decorada.

    :param name: Nome do span. Se omitido, usa o nome da função.
    :param kind: Tipo do span (INTERNAL, SERVER, etc.)
    :param attributes_from_args: Mapeia argumentos para atributos do span.
                                 Ex: {"user_id": "user.id"}
    :param static_attributes: Atributos fixos adicionais.
    """

    def build_span_attributes(func, args, kwargs):
        bound_args = inspect.signature(func).bind(*args, **kwargs)
        bound_args.apply_defaults()
        span_attributes = {
            "request.id": get_request_id(),
            "trace.id": get_trace_id(),
            **(static_attributes or {}),
        }
        if attributes_from_args:
            for arg_name, attr_name in attributes_from_args.items():
                if arg_name in bound_args.arguments:
                    span_attributes[attr_name] = bound_args.arguments[arg_name]
        return span_attributes

    def decorator(func: Callable[..., Any]):
        is_async = inspect.iscoroutinefunction(func)

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            span_name = name or func.__name__
            span_attributes = build_span_attributes(func, args, kwargs)
            tracer = get_tracer()
            with tracer.start_as_current_span(
                span_name, kind=kind, attributes=span_attributes
            ):
                return await func(*args, **kwargs)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            span_name = name or func.__name__
            span_attributes = build_span_attributes(func, args, kwargs)
            tracer = get_tracer()
            with tracer.start_as_current_span(
                span_name, kind=kind, attributes=span_attributes
            ):
                return func(*args, **kwargs)

        return async_wrapper if is_async else sync_wrapper

    return decorator
