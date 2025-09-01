# src/graph/fortify/base/factory.py
from typing import Any, Generic, Protocol, TypeVar

T = TypeVar("T")
C = TypeVar("C")


class FactoryProtocol(Protocol, Generic[T, C]):
    """
    An abstract base class for all factory implementations within the framework.

    It defines a standard interface for creating objects ('products') from a
    configuration object. This ensures architectural consistency across different
    modules of the Fortify framework.
    """

    @classmethod
    def create(cls, settings: C, **kwargs: Any) -> T:
        """
        Abstract method to create an instance of the product type 'T'.

        Subclasses must implement this method to provide the concrete logic
        for object creation based on the provided configuration.

        Args:
            config: The configuration object that guides the creation process.
            **kwargs: Additional optional parameters that might be needed by the factory,
                      such as a global `app_settings` instance.

        Returns:
            An instance of the product type T.
        """
        raise NotImplementedError
