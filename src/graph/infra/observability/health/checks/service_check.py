# Em: graph/fortify/observability/health/checks/service_check.py

from graph.infra.services.protocol import BaseServiceProtocol

from ..interfaces import ReadinessCheck


class ServiceReadinessCheck(ReadinessCheck):
    """
    A generic readiness check that can verify the health of any
    service implementing the BaseServiceProtocol.
    """

    def __init__(self, service: BaseServiceProtocol):
        """
        Args:
            service: The service instance to be monitored.
        """
        self._service = service
        # The check name is the same as the name of the service it monitors.
        self.name = self._service.service_name

    def enabled(self) -> bool:
        """Checks if the underlying service is enabled in the configuration."""
        return self._service.is_enabled()

    async def check(self) -> bool:
        """
        Checks if the service is ready to operate.
        Delegates the call directly to the service's is_ready() method.
        """
        return self._service.is_ready()
