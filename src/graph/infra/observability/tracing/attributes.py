# src/graph/fortify/observability/tracing/attributes.py
"""
Defines constants for OpenTelemetry span attribute names,
following semantic conventions for databases and other systems.
"""

# --- Database Attributes ---
DB_SYSTEM = "db.system"  # E.g.: "mongodb", "redis", "postgresql"
DB_OPERATION = "db.operation"  # E.g.: "save", "find_by_id", "delete"
DB_STATEMENT = "db.statement"  # The query or an identifier, e.g.: "id=123"
DB_KEY = "db.key"  # pragma: allowlist secret
DB_STATUS = "db.status"  # Operation status, e.g.: "hit", "miss"

# --- Storage Attributes ---
STORAGE_PROVIDER = "storage.provider"
STORAGE_DESTINATION_PATH = "storage.destination_path"
STORAGE_SOURCE_PATH = "storage.source_path"
STORAGE_PATH = "storage.path"
