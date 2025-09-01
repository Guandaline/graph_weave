# src/graph/fortify/observability/metrics/enums.py
from enum import Enum


class MetricStatus(str, Enum):
    """Defines standardized values for the 'status' label in metrics."""

    SUCCESS = "success"
    FAILURE = "failure"
    MISS = "miss"
    HIT = "hit"

    def __str__(self) -> str:
        return self.value


class DbOperation(str, Enum):
    """Defines standardized operation names for database metrics."""

    SAVE = "save"
    GET = "get"
    SET = "set"
    DELETE = "delete"
    FIND_ALL = "find_all"
    FIND_BY_ID = "find_by_id"
    FIND_BY_OWNER = "find_by_owner"
    EXISTS = "exists"
    CLEAR = "clear"
    IS_AVAILABLE = "is_available"
    ZADD = "zadd"
    ZREM = "zrem"
    ZPOPBYSCORE = "zpopbyscore"

    def __str__(self) -> str:
        return self.value


class FallbackReadStrategyType(str, Enum):
    """Defines read strategies for the FallbackKVProvider."""

    ON_ERROR = "on_error"
    ON_MISS_OR_ERROR = "on_miss_or_error"


class FallbackWriteStrategyType(str, Enum):
    """Defines write strategies for the FallbackKVProvider."""

    WRITE_AROUND = "write_around"
    WRITE_THROUGH = "write_through"
