# src/graph/fortify/config/schemas/app_settings.py
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ContextSettings(BaseModel):
    """Configuration settings for the context module."""

    model_config = ConfigDict(
        extra="ignore", validate_assignment=True, populate_by_name=True
    )

    multi_tenancy_enabled: Optional[bool] = Field(
        default=False,
        alias="MULTI_TENANCY_ENABLED",
        description="Enables automatic application of tenant_id filters in repositories.",
    )

    static_prefix: Optional[str] = Field(
        default="graph",
        alias="STATIC_PREFIX",
        description="Static prefix for keys.",
    )

    separator: Optional[str] = Field(
        default=":",
        alias="SEPARATOR",
        description="Separator for keys.",
    )

    namespace: Optional[str] = Field(
        default="default", alias="NAMESPACE", description="Namespace for keys."
    )

    use_user_uid: Optional[bool] = Field(
        default=False, alias="USE_USER_UID", description="Use user UID in keys."
    )

    propagated_vars: List[str] = Field(
        default_factory=lambda: [
            "request_id",
            "trace_id",
            "tenant_id",
            "span_id",
            "user_id",
            "role",
            "locale",
            "correlation_id",
            "feature_flags",
        ],
        alias="PROPAGATED_VARS",
        description="List of context variable names to propagate to background tasks and events.",
    )
