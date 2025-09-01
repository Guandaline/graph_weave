# graph/fortify/context/manager.py

from contextvars import ContextVar, Token
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from graph.infra.observability import logger


@dataclass
class ContextVarInfo:
    """Stores the ContextVar and its metadata."""

    var: ContextVar
    propagate: bool = False
    default: Any = None


class ContextVarManager:
    """Manages the registration and access to all application ContextVars."""

    def __init__(self):
        self._vars: Dict[str, ContextVarInfo] = {}

    def register(
        self, name: str, propagate: bool = False, default: Optional[Any] = None
    ) -> None:
        """Registers a new ContextVar in the manager."""

        if name in self._vars:
            logger.warning(f"Context variable '{name}' is being overwritten.")

        logger.debug(f"Registering context variable '{name}' with default '{default}'")

        self._vars[name] = ContextVarInfo(
            var=ContextVar(name, default=default), propagate=propagate, default=default
        )

        logger.trace(f"Context variable '{name}' registered (propagate={propagate}).")

    def get(self, name: str, default: Optional[Any] = None) -> Any:
        """Gets the value of a ContextVar."""
        info = self._vars.get(name)
        return info.var.get(default) if info else default

    def set(self, name: str, value: Any) -> Optional[Token]:
        """Sets the value of a ContextVar."""
        info = self._vars.get(name)

        if info:
            return info.var.set(value)

        logger.warning(f"Attempted to set unregistered context variable '{name}'.")
        return None

    def reset(self, name: str, token: Token) -> None:
        """Resets a ContextVar using its token."""

        info = self._vars.get(name)

        if info:
            info.var.reset(token)

    def get_propagated_vars(self) -> Dict[str, ContextVarInfo]:
        """Returns a dictionary of all vars marked for propagation."""
        return {name: info for name, info in self._vars.items() if info.propagate}

    def get_all_vars(self) -> Dict[str, ContextVarInfo]:
        """Returns all registered vars."""
        return self._vars

    def register_from_definitions(
        self, var_definitions: List[Tuple[str, Any]], vars_to_propagate: List[str]
    ) -> None:
        """
        Iterates over a list of variable definitions and registers them.

        Args:
            var_definitions: A list of tuples, where each tuple is (name, default_value).
            vars_to_propagate: A list of variable names that should have propagate=True.
        """
        logger.debug("Registering context variables from definitions.")
        for name, default_value in var_definitions:
            self.register(
                name=name, propagate=(name in vars_to_propagate), default=default_value
            )

    def get_current_context_dict(self) -> Dict[str, Any]:
        """Returns a dictionary with the state of all context variables."""
        all_vars = context_var_manager.get_all_vars()
        return {name: info.var.get() for name, info in all_vars.items()}

    def clear_all_context(self) -> None:
        """Clears all context variables to their default values."""
        logger.debug("Clearing all context variables to their default values.")
        all_vars = context_var_manager.get_all_vars()

        for name, info in all_vars.items():
            logger.debug(f"Resetting context variable '{name}' to default.")
            info.var.set(info.default)
            logger.trace(
                f"Context variable '{name}' reset to default value '{info.default}'."
            )


# Singleton instance
context_var_manager = ContextVarManager()
