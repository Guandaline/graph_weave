# config/schemas/observability_config.py
from typing import Dict, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from .metrics_config import MetricsSettings


class ObservabilitySettings(BaseModel):
    """Settings for Metrics (Prometheus) and Tracing (OTLP)."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    # --- General Observability Settings ---
    enabled: bool = Field(
        default=True,
        description="Globally enables/disables observability features (metrics, tracing).",
    )

    # --- Prometheus Exporter Settings ---
    exporter_enabled: bool = Field(
        default=True,  # Allows disabling only the exporter, even with observability=True
        description="Enables/disables the Prometheus metrics server at /metrics.",
    )
    exporter_port: int = Field(
        default=9100,
        description="Port where the Prometheus metrics server will listen.",
    )

    # --- Tracing (OpenTelemetry) Settings ---
    tracing_enabled: bool = Field(
        default=True,
        description="Enables/disables sending OpenTelemetry traces.",
    )
    otlp_endpoint: Optional[str] = Field(
        default=None,  # E.g.: "http://localhost:4317" or "otel-collector.namespace:4317"
        description="OTLP endpoint (gRPC or HTTP) to send traces.",
    )
    otlp_protocol: Literal["grpc", "http/protobuf"] = Field(
        default="grpc",
        description="Protocol to use for exporting OTLP traces (grpc or http/protobuf).",
    )
    otlp_headers: Optional[Dict[str, str]] = Field(
        default=None,
        description="Additional headers to send to the OTLP endpoint (e.g., authentication).",
    )
    # The service name usually comes from the main app_name, but can be overridden
    service_name_override: Optional[str] = Field(
        default=None,
        description="Optional: Overrides the service name for tracing.",
    )
    sampling_rate: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Sampling rate for traces (0.0 to 1.0).",
    )

    metrics: Optional[MetricsSettings] = Field(
        default_factory=MetricsSettings,
        alias="METRICS",
        description="Specific settings for metrics, such as Prometheus.",
    )
