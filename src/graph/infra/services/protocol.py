from typing import Protocol, runtime_checkable


@runtime_checkable
class BaseServiceProtocol(Protocol):
    """
    Protocol for a manageable service with a defined base service.
    """

    def is_ready(self) -> bool:
        """
        Returns True if the service has successfully completed its startup.
        """
        ...

    async def start(self) -> None:
        """
        Initializes the service and prepares it for use.
        """
        ...

    async def stop(self) -> None:
        """
        Gracefully shuts down the service and cleans up resources.
        """
        ...
