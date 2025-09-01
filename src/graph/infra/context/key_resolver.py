import hashlib
import json
from typing import Any, Callable, Dict, List, Optional, Tuple

from loguru import logger

from graph.infra.config import get_settings
from graph.infra.config.schemas.context.context_config import ContextSettings
from graph.infra.context.execution import ExecutionContext


def _default_arg_serializer(obj: Any) -> str:
    """Fallback serializer for non-JSON-serializable function arguments."""
    try:
        return repr(obj)
    except Exception:
        return f"<unserializable type: {type(obj).__name__}>"


class ContextualKeyGenerator:
    """
    Centralized service to create consistent and context-sensitive keys.
    """

    def __init__(
        self,
        *,
        namespace: Optional[str] = None,
        settings: Optional[ContextSettings] = None,
    ):
        self.settings: ContextSettings = settings or get_settings().context

        self.static_prefix: str = self.settings.static_prefix or "graph"

        self.use_tenant: bool = (
            self.settings.multi_tenancy_enabled
            if self.settings.multi_tenancy_enabled is not None
            else True
        )
        self.use_user: bool = (
            self.settings.use_user_uid
            if self.settings.use_user_uid is not None
            else False
        )

        self.separator: str = self.settings.separator or ":"
        self.namespace: str = namespace or self.settings.namespace or "default"

    def _get_context_prefix(self) -> str:
        """Builds the contextual part of the key (e.g., 'tenant1:user42')."""
        current_context = ExecutionContext()
        parts: List[str] = []

        if self.use_tenant and current_context.tenant_id:
            parts.append(current_context.tenant_id)

        if self.use_user and current_context.user_id:
            parts.append(current_context.user_id)

        return self.separator.join(parts)

    def generate(self, *key_parts: Any) -> str:
        """
        Generates a key from multiple parts, applying context and namespace prefixes.
        """
        context_prefix = self._get_context_prefix()

        all_parts = [
            self.static_prefix,
            context_prefix,
            self.namespace,
            *(str(p) for p in key_parts if p is not None),
        ]

        return self.separator.join(filter(None, all_parts))

    def generate_for_function(self, func: Callable, args: Tuple, kwargs: Dict) -> str:
        """
        Generates a unique and deterministic key for a function decorator.
        """
        function_name = getattr(func, "__qualname__", str(func))

        try:
            kwargs_tuple = tuple(sorted(kwargs.items()))
            combined_args = (args, kwargs_tuple)
            serialized_args = json.dumps(
                combined_args, sort_keys=True, default=_default_arg_serializer
            )
            hashed_args = hashlib.sha256(serialized_args.encode("utf-8")).hexdigest()
        except Exception:
            logger.exception("Error serializing/hashing key arguments.")
            hashed_args = "hashing_error"

        return self.generate(function_name, hashed_args)
