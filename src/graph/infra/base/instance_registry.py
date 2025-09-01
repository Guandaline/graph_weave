# src/graph/fortify/base/registry.py
from typing import Dict, Generic, Optional, Type, TypeVar

from loguru import logger

T = TypeVar("T")


class BaseInstanceRegistry(Generic[T]):
    """
    A base class for registries that store INSTANCES of objects
    that adhere to a specific protocol.
    """

    def __init__(self, protocol: Optional[Type[T]] = None):
        self._registry: Dict[str, T] = {}
        self._protocol = protocol
        self.logger = logger

    def register(self, name: str, item_instance: T):
        """
        Registers an object instance with a specific name.
        Validates if the instance adheres to the registry's protocol.
        """
        if self._protocol and not isinstance(item_instance, self._protocol):
            raise TypeError(
                f"The instance '{item_instance.__class__.__name__}' does not implement the protocol '{self._protocol.__name__}'."
            )

        if name in self._registry:
            logger.warning(
                f"Overwriting existing instance '{name}' in the registry with a new instance of type '{item_instance.__class__.__name__}'."
            )

        self._registry[name] = item_instance

    def get(self, name: str) -> Optional[T]:
        """Fetches a registered instance by name."""
        return self._registry.get(name)

    def all(self) -> Dict[str, T]:
        """Returns all registered instances."""
        return self._registry

    async def clear(self) -> None:
        """Clears the registry, stopping all services."""
        for service in self._registry.values():
            if hasattr(service, "stop"):
                await service.stop()
            elif hasattr(service, "close"):
                await service.close()
        logger.info("Clearing registry and stopping all services.")
        self._registry.clear()

    def remove(self, name: str) -> Optional[T]:
        """Removes an item from the registry by its name."""
        name = name.lower()
        item_instance = self._registry.get(name)
        if item_instance:
            self.logger.debug(f"Removing {item_instance.__class__.__name__}: {name}")
            return self._registry.pop(name)
        self.logger.warning(
            f"Attempted to remove a non-existent {item_instance.__class__.__name__}: {name}"
        )
        return None
