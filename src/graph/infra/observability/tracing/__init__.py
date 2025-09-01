from opentelemetry.trace import SpanKind, StatusCode  # <<< Importar aqui

from .tracing import Tracer, get_current_span, get_tracer, setup_tracing

__all__ = [
    "get_tracer",
    "get_current_span",
    "setup_tracing",
    "StatusCode",
    "SpanKind",
    "Tracer",
]
