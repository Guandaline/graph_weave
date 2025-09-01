from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class MetricsSettings(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    enabled: Optional[bool] = Field(
        default=True,
        alias="ENABLED",
        description="Enables or disables metrics collection.",
    )

    collection_interval_seconds: int = Field(
        default=60,
        ge=1,
        description="Interval in seconds for metrics collection.",
        alias="COLLECTION_INTERVAL_SECONDS",
    )
