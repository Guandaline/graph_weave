import functools
import inspect
from typing import Any, Callable, Dict, Optional

from loguru import logger
from opentelemetry import context, trace
from opentelemetry.trace import SpanKind, StatusCode

from graph.infra.context.context_vars import get_request_id, get_trace_id
from graph.infra.observability.tracing import get_tracer


def build_span_attributes(
    bound_args, static_attributes, attributes_from_args
) -> Dict[str, Any]:
    span_attributes = {
        "request.id": get_request_id(),
        "trace.id": get_trace_id(),
        **(static_attributes or {}),
    }
    if attributes_from_args:
        for arg_name, attr_name in attributes_from_args.items():
            if arg_name in bound_args.arguments:
                span_attributes[attr_name] = bound_args.arguments[arg_name]
    return {k: v for k, v in span_attributes.items() if v is not None}


def log_call(logger, func_name: str, args, kwargs):
    logger.info(
        f"{func_name} called",
        extra={
            "args": args,
            "kwargs": kwargs,
            "trace_id": get_trace_id(),
            "request_id": get_request_id(),
        },
    )


def log_result(logger, func_name: str, result):
    logger.info(
        f"{func_name} returned",
        extra={
            "result": result,
            "trace_id": get_trace_id(),
            "request_id": get_request_id(),
        },
    )


def log_error(logger, func_name: str, error: Exception):
    logger.error(
        f"{func_name} error: {error}",
        extra={
            "trace_id": get_trace_id(),
            "request_id": get_request_id(),
        },
        exc_info=True,
    )


def with_observability(
    name: Optional[str] = None,
    kind: SpanKind = SpanKind.INTERNAL,
    attributes_from_args: Optional[Dict[str, str]] = None,
    static_attributes: Optional[Dict[str, Any]] = None,
    should_log_result: bool = True,
    log_args: bool = True,
) -> Callable[..., Any]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        is_async = inspect.iscoroutinefunction(func)

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            tracer = get_tracer()
            span_name = name or func.__name__
            bound_args = inspect.signature(func).bind(*args, **kwargs)
            bound_args.apply_defaults()
            span_attributes = build_span_attributes(
                bound_args, static_attributes, attributes_from_args
            )
            if log_args:
                log_call(logger, func.__name__, args, kwargs)
            span = tracer.start_span(span_name, kind=kind, attributes=span_attributes)
            token = context.attach(trace.set_span_in_context(span))
            try:
                result = await func(*args, **kwargs)
                span.set_status(StatusCode.OK)
                if should_log_result:
                    log_result(logger, func.__name__, result)
                return result
            except Exception as e:
                span.record_exception(e)
                span.set_status(StatusCode.ERROR, description=str(e))
                log_error(logger, func.__name__, e)
                raise
            finally:
                span.end()
                context.detach(token)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            tracer = get_tracer()
            span_name = name or func.__name__
            bound_args = inspect.signature(func).bind(*args, **kwargs)
            bound_args.apply_defaults()
            span_attributes = build_span_attributes(
                bound_args, static_attributes, attributes_from_args
            )
            if log_args:
                log_call(logger, func.__name__, args, kwargs)
            with tracer.start_as_current_span(
                span_name, kind=kind, attributes=span_attributes
            ) as span:
                try:
                    result = func(*args, **kwargs)
                    span.set_status(StatusCode.OK)
                    if should_log_result:
                        log_result(logger, func.__name__, result)
                    return result
                except Exception as e:
                    span.record_exception(e)
                    span.set_status(StatusCode.ERROR, description=str(e))
                    log_error(logger, func.__name__, e)
                    raise

        return async_wrapper if is_async else sync_wrapper

    return decorator
