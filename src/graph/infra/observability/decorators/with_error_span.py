import functools
import inspect
from typing import Any, Callable, Optional

from opentelemetry.trace import SpanKind, StatusCode

from graph.infra.context.context_vars import get_request_id, get_trace_id
from graph.infra.observability.tracing import get_tracer


def _build_span_attributes(func, args, kwargs, static_attributes, attributes_from_args):
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


def _handle_exception(span, exc):
    span.record_exception(exc)
    span.set_status(StatusCode.ERROR)
    raise exc


def with_span_and_error_capture(
    name: Optional[str] = None,
    kind: SpanKind = SpanKind.INTERNAL,
    attributes_from_args: Optional[dict[str, str]] = None,
    static_attributes: Optional[dict[str, str]] = None,
) -> Callable[..., Any]:
    def decorator(func: Callable[..., Any]):
        is_async = inspect.iscoroutinefunction(func)

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            tracer = get_tracer()
            span_name = name or func.__name__
            span_attributes = _build_span_attributes(
                func, args, kwargs, static_attributes, attributes_from_args
            )
            async with tracer.start_as_current_span(
                span_name, kind=kind, attributes=span_attributes
            ) as span:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    _handle_exception(span, e)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            tracer = get_tracer()
            span_name = name or func.__name__
            span_attributes = _build_span_attributes(
                func, args, kwargs, static_attributes, attributes_from_args
            )
            with tracer.start_as_current_span(
                span_name, kind=kind, attributes=span_attributes
            ) as span:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    _handle_exception(span, e)

        return async_wrapper if is_async else sync_wrapper

    return decorator
