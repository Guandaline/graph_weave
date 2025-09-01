import asyncio
from abc import ABC, abstractmethod

from .protocol import BaseServiceProtocol


class BaseService(BaseServiceProtocol, ABC):
    """
    A simplified version of the Fortify BaseService.
    Manages the lifecycle and readiness state of a service.
    """

    def __init__(self, service_name: str):
        self.service_name = service_name
        self._ready = asyncio.Event()
        self._is_closed = False

    async def start(self) -> None:
        """
        Starts the service by calling its internal connect method.
        """
        if self._is_closed:
            raise RuntimeError(f"Service '{self.service_name}' is already closed.")

        # We only connect if we are not already ready
        if not self._ready.is_set():
            await self._connect()
            self._ready.set()
            print(f"Service '{self.service_name}' is now READY.")

    async def stop(self) -> None:
        """
        Stops the service gracefully by calling its internal close method.
        """
        if self._is_closed:
            return

        self._ready.clear()
        await self._close()
        self._is_closed = True
        print(f"Service '{self.service_name}' has been stopped.")

    def is_ready(self) -> bool:
        """
        Returns True if the service has completed its startup and is ready to be used.
        """
        return self._ready.is_set()

    @abstractmethod
    async def _connect(self) -> None:
        """
        Subclasses must implement this method to establish a connection or perform startup logic.
        """
        pass

    @abstractmethod
    async def _close(self) -> None:
        """
        Subclasses must implement this method to gracefully close connections or clean up resources.
        """
        pass
