"""graph.infra.context

This package is responsible for managing execution context in a thread-safe and async-safe way.

It includes:
- `context_vars`: fine-grained control of per-request variables (e.g. tenant_id, request_id, trace_id)
- `ExecutionContext`: a centralized object that encapsulates all context variables
- `ContextualKeyGenerator`: a utility for generating consistent keys based on the execution context

All Fortify modules should rely on this package for:
- Multi-tenancy support
- Structured logging enrichment
- Distributed tracing propagation
- Per-user/session rate limiting and caching
- Test isolation and context cleanup
"""

from . import context_vars
from .execution import ExecutionContext
from .key_resolver import ContextualKeyGenerator
from .manager import ContextVarInfo, ContextVarManager, context_var_manager
from .propagation import capture_context, restore_context

__all__ = [
    "context_vars",
    "ExecutionContext",
    "ContextualKeyGenerator",
    "capture_context",
    "restore_context",
    "context_var_manager",
    "ContextVarManager",
    "ContextVarInfo",
]
