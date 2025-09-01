from functools import lru_cache
from typing import Any, Dict, Optional

from dynaconf import Dynaconf
from loguru import logger
from pydantic import ValidationError

from .providers.dynaconf_loader import DynaconfLoader
from .schemas.app_settings import AppSettings


@lru_cache()
def get_settings() -> AppSettings:
    """Loads, validates, and returns the settings instance (cached)."""
    logger.debug("Calling _load_and_validate_settings to get/cache settings.")
    return _load_and_validate_settings()


def _load_and_validate_settings() -> AppSettings:
    """Orchestrates loading with Dynaconf and validation with Pydantic."""
    logger.debug("--- DEBUG: Running _load_and_validate_settings ---")

    logger.info("Loading raw configuration using DynaconfLoader...")
    raw_config_dict: Dict[str, Any] = {}
    dynaconf_instance: Optional[Dynaconf] = None

    try:
        loader = DynaconfLoader()
        dynaconf_instance = loader.load()
        current_env = dynaconf_instance.current_env
        raw_config_dict = dynaconf_instance.as_dict(env=current_env)
        logger.debug(
            f"--- DEBUG: Raw config dict loaded by Dynaconf for env '{current_env}': {raw_config_dict}"
        )

    except Exception as e:
        logger.exception("Failed to load configuration via DynaconfLoader.")
        raise RuntimeError("Application configuration could not be loaded.") from e

    if not raw_config_dict and dynaconf_instance:
        logger.warning(
            f"Dynaconf loaded successfully but resulting dictionary for env '{dynaconf_instance.current_env}' is empty."
        )
        raw_config_dict = {}

    logger.info("Validating configuration using Pydantic schema (AppSettings)...")

    try:
        dict_to_pass = raw_config_dict.copy()

        logger.debug(
            f"--- DEBUG: [Pydantic Check] Keys in dict: {list(dict_to_pass.keys())}"
        )

        validated_settings = AppSettings(**dict_to_pass)
        logger.debug(
            f"--- DEBUG: Pydantic validation successful. App Name: '{validated_settings.app_name}'"
        )
        logger.success("Configuration loaded and validated successfully!")
        return validated_settings
    except ValidationError as e:
        logger.error(f"Pydantic validation failed! Errors:\n{e}")
        raise ValueError(f"Application configuration validation failed: {e}") from e
    except Exception as e:
        logger.exception("An unexpected error occurred during Pydantic validation.")
        raise ValueError(
            "Application configuration validation failed (Unexpected)."
        ) from e
