# src/graph/fortify/config/schemas/app_settings.py
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from graph.infra.config.schemas.store.store_config import StoreSettings

from .context.context_config import ContextSettings
from .observability.observability_config import ObservabilitySettings


class AppSettings(BaseModel):
    model_config = ConfigDict(
        extra="ignore", validate_assignment=True, populate_by_name=True
    )

    enabled: bool = Field(default=True, alias="ENABLED")
    app_name: str = Field(..., alias="APP_NAME")
    env: Literal["default", "development", "staging", "production"] = Field(
        default="default", alias="ENV", description="Application environment"
    )

    timeout: Optional[float] = Field(
        default=30.0,
        alias="TIMEOUT",
        description="Timeout for connecting to external services in seconds.",
    )

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    tags: List[str] = Field(default_factory=list, alias="TAGS")

    context: Optional[ContextSettings] = Field(
        default_factory=ContextSettings,
        alias="CONTEXT",
        description="Context settings for the application.",
    )

    observability: Optional[ObservabilitySettings] = Field(
        default_factory=ObservabilitySettings, alias="OBSERVABILITY"
    )

    store: StoreSettings = Field(default_factory=StoreSettings, alias="STORE")


AppSettings.model_rebuild()
