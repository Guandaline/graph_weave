from typing import Any, Dict, Optional

from graph.infra.context import context_vars


class ExecutionContext:
    def __init__(
        self,
        tenant_id: Optional[str] = None,
        request_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None,
        user_id: Optional[str] = None,
        role: Optional[str] = None,
        locale: Optional[str] = None,
        source_ip: Optional[str] = None,
        session_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        feature_flags: Optional[Dict[str, bool]] = None,
    ):
        self.tenant_id = tenant_id or context_vars.get_tenant_id()
        self.request_id = request_id or context_vars.get_request_id()
        self.trace_id = trace_id or context_vars.get_trace_id()
        self.span_id = span_id or context_vars.get_span_id()
        self.user_id = user_id or context_vars.get_user_id()
        self.role = role or context_vars.get_role()
        self.locale = locale or context_vars.get_locale()
        self.source_ip = source_ip or context_vars.get_source_ip()
        self.session_id = session_id or context_vars.get_session_id()
        self.correlation_id = correlation_id or context_vars.get_correlation_id()
        self.feature_flags = feature_flags or context_vars.get_feature_flags()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tenant_id": self.tenant_id,
            "request_id": self.request_id,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "user_id": self.user_id,
            "role": self.role,
            "locale": self.locale,
            "source_ip": self.source_ip,
            "session_id": self.session_id,
            "correlation_id": self.correlation_id,
            "feature_flags": self.feature_flags,
        }

    def __repr__(self) -> str:
        return f"ExecutionContext({self.to_dict()})"
