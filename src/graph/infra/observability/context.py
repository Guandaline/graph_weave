# In: graph/fortify/observability/context.py
from dataclasses import dataclass


@dataclass(frozen=True)
class TraceContext:
    """
    An agnostic data contract for trace propagation.

    This object represents the essential, transport-independent information
    required for distributed tracing.
    """

    trace_id: str | None
    # Future fields like span_id or parent_id can be added here.
