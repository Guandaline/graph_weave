# src/graph/fortify/base/registry.py
import inspect
from abc import ABC
from typing import Callable, Dict, Generic, Optional, Type, TypeVar

from loguru import logger

T = TypeVar("T")


class BaseRegistry(ABC, Generic[T]):
    """
    A base class for creating provider registries, with decorator support.
    The logic is now instance-based to allow clearer encapsulation
    and a clean decorator syntax.
    """

    def __init__(self, protocol: Type[T]):
        """
        Initializes a new registry instance.
        Each instance will have its own dictionary of items.
        """
        self._registry: Dict[str, Type[T]] = {}
        self._protocol = protocol
        logger.debug(
            f"Instance of {self.__class__.__name__} created for protocol {protocol.__name__}."
        )
        self.register_defaults()

    def register(
        self, name: str, item_class: Optional[Type[T]] = None
    ) -> Optional[Callable[[Type[T]], Type[T]]]:
        """
        Registers an item, can be used directly or as a decorator.

        Direct Use:
            registry.register("my_item", MyItemClass)

        As a Decorator:
            @registry.register("my_item")
            class MyItemClass:
                ...
        """
        if item_class is None:

            def decorator(cls_to_register: Type[T]) -> Type[T]:
                self._register_item(name, cls_to_register)
                return cls_to_register

            return decorator

        self._register_item(name, item_class)
        return None

    def _register_item(self, name: str, item_class: Type[T]) -> None:
        """Internal logic for validation and registration."""
        normalized_name = name.lower()

        item_class_name = (
            item_class.__name__
            if inspect.isclass(item_class)
            else item_class.__class__.__name__
        )

        logger.info(
            f"Registered '{normalized_name}' -> {item_class_name} in {self.__class__.__name__}."
        )
        self._registry[normalized_name] = item_class

    def get(self, name: str) -> T:
        """
        Retrieves a registered item by its name.

        Args:
            name: The name of the item to retrieve.

        Returns:
            The registered item.

        Raises:
            ValueError: If no item is registered with the given name.
        """
        key = name.lower()
        if key not in self._registry:
            raise ValueError(
                f"Item '{name}' is not registered in {self.__class__.__name__}."
            )
        return self._registry[key]

    def clear(self) -> None:
        """Clears the registry. Useful for testing."""
        self._registry.clear()

    def get_all(self) -> Dict[str, Type[T]]:
        """
        Returns all registered items.

        Returns:
            A dictionary of all registered items.
        """
        return self._registry.copy()

    def register_defaults(self) -> None:
        """
        Method that forces subclasses to register their default items.
        It is automatically called by the constructor.
        """
        ...
