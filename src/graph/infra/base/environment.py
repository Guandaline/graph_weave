from enum import Enum
from functools import lru_cache

# Import the centralized settings object from your project
from graph.infra.config import get_settings

app_settings = get_settings()


class AppEnvironment(str, Enum):
    """
    Enum to represent the possible environments of the application.

    Inherits from `str` so it can be directly compared with strings if needed.
    """

    PRODUCTION = "production"
    STAGING = "staging"
    DEVELOPMENT = "development"
    TESTING = "testing"
    DEFAULT = "default"


@lru_cache(maxsize=1)
def get_current_environment() -> AppEnvironment:
    """
    Returns the current environment of the application based on the settings.

    Uses lru_cache so the configuration is read only once,
    improving performance.
    """
    env_str = app_settings.env.lower()
    return AppEnvironment(env_str)


def is_production() -> bool:
    """
    Checks if the current environment is production.

    Returns True if the environment is 'production', otherwise returns False.
    """
    return get_current_environment() == AppEnvironment.PRODUCTION
