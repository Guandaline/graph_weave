from typing import Any, Dict, Optional

from loguru import logger
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import \
    OTLPSpanExporter
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased
from opentelemetry.trace import Span, SpanKind, Status, StatusCode, Tracer

from graph.infra.config import get_settings
from graph.infra.config.schemas import ObservabilitySettings
from graph.infra.config.schemas.app_settings import AppSettings
from graph.infra.context.context_vars import get_request_id, get_trace_id

_tracing_initialized = False


def setup_tracing(settings: Optional[AppSettings] = None) -> None:
    global _tracing_initialized
    if _tracing_initialized:
        logger.debug("OpenTelemetry Tracing already initialized.")
        return

    try:
        settings: AppSettings = settings or get_settings()
        obs_settings: Optional[ObservabilitySettings] = settings.observability
    except Exception as e:
        logger.error(f"Failed to load settings for tracing configuration: {e}")
        obs_settings = None

    if not obs_settings or not obs_settings.enabled or not obs_settings.tracing_enabled:
        logger.info("OpenTelemetry Tracing is disabled in the configuration.")
        _tracing_initialized = True
        return

    exporter = None
    if not obs_settings.otlp_endpoint:
        logger.warning(
            "OTLP endpoint not configured (OBSERVABILITY__OTLP_ENDPOINT). "
            "Tracing SDK initialized, but spans will not be exported."
        )
    else:
        logger.info(
            f"Configuring OTLP Exporter for: {obs_settings.otlp_endpoint} (Protocol: {obs_settings.otlp_protocol})"
        )
        exporter = OTLPSpanExporter(
            endpoint=obs_settings.otlp_endpoint,
            insecure=True,
            headers=obs_settings.otlp_headers,
        )

    service_name = obs_settings.service_name_override or settings.app_name or "graph"
    resource = Resource(attributes={SERVICE_NAME: service_name})
    logger.info(f"Setting OpenTelemetry service name to: '{service_name}'")

    try:
        sampling_rate = float(obs_settings.sampling_rate)
        sampler = TraceIdRatioBased(sampling_rate)
        logger.info(f"Setting OpenTelemetry sampling rate to: {sampling_rate}")
    except ValueError:
        logger.error(
            f"Invalid value for sampling_rate: '{obs_settings.sampling_rate}'. Using default 1.0."
        )
        sampler = TraceIdRatioBased(1.0)

    provider = TracerProvider(resource=resource, sampler=sampler)
    if exporter:
        processor = BatchSpanProcessor(exporter)
        provider.add_span_processor(processor)
        logger.info("OTLP Span Exporter added to TracerProvider.")
    else:
        logger.warning(
            "No OTLP exporter configured, spans will not be sent to a backend."
        )

    trace.set_tracer_provider(provider)
    logger.info("OpenTelemetry TracerProvider set as global.")

    logger.info("Instrumenting libraries for OpenTelemetry...")
    try:
        LoggingInstrumentor().instrument(set_logging_format=False)
        logger.debug("Logging instrumented.")
        RequestsInstrumentor().instrument()
        logger.debug("Requests instrumented.")
    except Exception as e:
        logger.error(f"Failed to instrument libraries: {e}")

    _tracing_initialized = True
    logger.success("OpenTelemetry Tracing SDK and instrumentors configured.")


def get_tracer(name: Optional[str] = None) -> Tracer:
    effective_name = name
    if not effective_name:
        try:
            settings = get_settings()
            obs_settings = settings.observability
            effective_name = (
                (obs_settings.service_name_override if obs_settings else None)
                or settings.app_name
                or "graph"
            )
        except Exception:
            effective_name = "graph"

    return trace.get_tracer(effective_name)


def start_span(
    name: str,
    kind: SpanKind = SpanKind.INTERNAL,
    attributes: Optional[Dict[str, Any]] = None,
) -> trace.Span:
    tracer = get_tracer()
    ctx_attributes: Dict[str, Any] = {}
    try:
        req_id = get_request_id()
        trace_id = get_trace_id()
        if req_id:
            ctx_attributes["request.id"] = req_id
        if trace_id:
            ctx_attributes["trace.id.explicit"] = trace_id
    except LookupError:
        logger.trace(
            "Context variables (request_id, trace_id) not found for span attributes."
        )
    except Exception as e:
        logger.warning(
            f"Could not retrieve request/trace context for span attributes: {e}"
        )

    if attributes:
        ctx_attributes.update(attributes)

    final_attributes = {
        k: v for k, v in ctx_attributes.items() if v is not None
    } or None

    span = tracer.start_span(name=name, kind=kind, attributes=final_attributes)
    return span


def set_span_status_ok(span: Span, message: str = "OK") -> None:
    span.set_status(Status(StatusCode.OK, message))


def set_span_status_error(
    span: Span, message: str, record_exception: bool = True
) -> None:
    if record_exception:
        span.record_exception(None)
    span.set_status(Status(StatusCode.ERROR, message))


def get_current_span() -> Span:
    """
    Returns the active span in the current execution context.

    This is a wrapper over the direct OpenTelemetry call to maintain
    abstraction and avoid requiring the application code to import 'opentelemetry'.
    """
    return trace.get_current_span()
