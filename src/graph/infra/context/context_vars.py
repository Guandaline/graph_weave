# graph/fortify/context/context_vars.py

from contextvars import Token
from typing import Any, Dict, Optional

from graph.infra.config.settings import get_settings

from .manager import context_var_manager

_ALL_CONTEXT_VARS = [
    ("request_id", None),
    ("trace_id", None),
    ("tenant_id", None),
    ("span_id", None),
    ("user_id", None),
    ("role", None),
    ("locale", "pt-BR"),
    ("source_ip", None),
    ("session_id", None),
    ("correlation_id", None),
    ("feature_flags", {}),
    ("timeout_deadline", None),
    ("timeout_cancelled", False),
]

_context_settings = get_settings().context

context_var_manager.register_from_definitions(
    var_definitions=_ALL_CONTEXT_VARS,
    vars_to_propagate=_context_settings.propagated_vars,
)

# --- Access Functions (Getters/Setters) ---


def get_request_id() -> Optional[str]:
    return context_var_manager.get("request_id")


def set_request_id(value: Optional[str]) -> Token:
    return context_var_manager.set("request_id", value)


def get_trace_id() -> Optional[str]:
    return context_var_manager.get("trace_id")


def set_trace_id(value: Optional[str]) -> Token:
    return context_var_manager.set("trace_id", value)


def get_tenant_id() -> Optional[str]:
    return context_var_manager.get("tenant_id")


def set_tenant_id(value: Optional[str]) -> Token:
    return context_var_manager.set("tenant_id", value)


def get_span_id() -> Optional[str]:
    return context_var_manager.get("span_id")


def set_span_id(value: Optional[str]) -> Token:
    return context_var_manager.set("span_id", value)


def get_user_id() -> Optional[str]:
    return context_var_manager.get("user_id")


def set_user_id(value: Optional[str]) -> Token:
    return context_var_manager.set("user_id", value)


def get_role() -> Optional[str]:
    return context_var_manager.get("role")


def set_role(value: Optional[str]) -> Token:
    return context_var_manager.set("role", value)


def get_locale() -> str:
    return context_var_manager.get("locale")


def set_locale(value: str) -> Token:
    return context_var_manager.set("locale", value)


def get_source_ip() -> Optional[str]:
    return context_var_manager.get("source_ip")


def set_source_ip(value: Optional[str]) -> Token:
    return context_var_manager.set("source_ip", value)


def get_session_id() -> Optional[str]:
    return context_var_manager.get("session_id")


def set_session_id(value: Optional[str]) -> Token:
    return context_var_manager.set("session_id", value)


def get_correlation_id() -> Optional[str]:
    return context_var_manager.get("correlation_id")


def set_correlation_id(value: Optional[str]) -> Token:
    return context_var_manager.set("correlation_id", value)


def get_feature_flags() -> Dict[str, bool]:
    return context_var_manager.get("feature_flags")


def set_feature_flags(value: Dict[str, bool]) -> Token:
    return context_var_manager.set("feature_flags", value)


def get_timeout_deadline() -> Optional[float]:
    return context_var_manager.get("timeout_deadline")


def set_timeout_deadline(value: Optional[float]) -> Token:
    return context_var_manager.set("timeout_deadline", value)


def is_timeout_cancelled() -> bool:
    return context_var_manager.get("timeout_cancelled")


def set_timeout_cancelled(value: bool) -> Token:
    return context_var_manager.set("timeout_cancelled", value)


def get_current_context_dic() -> Dict[str, Any]:
    """Returns a dictionary with the state of all context variables."""
    return context_var_manager.get_current_context_dict()


def clear_all_context() -> None:
    """Clears all context variables to their default values."""
    context_var_manager.clear_all_context()


def clear_request_id() -> None:
    """Clears the request_id context variable."""
    context_var_manager.set("request_id", None)


def clear_trace_id() -> None:
    """Clears the trace_id context variable."""
    context_var_manager.set("trace_id", None)


def clear_tenant_id() -> None:
    """Clears the tenant_id context variable."""
    context_var_manager.set("tenant_id", None)


def clear_span_id() -> None:
    """Clears the span_id context variable."""
    context_var_manager.set("span_id", None)


def clear_user_id() -> None:
    """Clears the user_id context variable."""
    context_var_manager.set("user_id", None)


def clear_role() -> None:
    """Clears the role context variable."""
    context_var_manager.set("role", None)


def clear_locale() -> None:
    """Resets the locale context variable to its default ('pt-BR')."""
    context_var_manager.set("locale", "pt-BR")


def clear_source_ip() -> None:
    """Clears the source_ip context variable."""
    context_var_manager.set("source_ip", None)


def clear_session_id() -> None:
    """Clears the session_id context variable."""
    context_var_manager.set("session_id", None)


def clear_correlation_id() -> None:
    """Clears the correlation_id context variable."""
    context_var_manager.set("correlation_id", None)


def clear_feature_flags() -> None:
    """Resets the feature_flags context variable to an empty dict."""
    context_var_manager.set("feature_flags", {})


def clear_timeout_deadline() -> None:
    """Clears the timeout_deadline context variable."""
    context_var_manager.set("timeout_deadline", None)


def clear_timeout_cancelled() -> None:
    """Resets the timeout_cancelled flag to False."""
    context_var_manager.set("timeout_cancelled", False)
