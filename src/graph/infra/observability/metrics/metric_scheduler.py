# src/graph/fortify/observability/metrics/metric_scheduler.py
import asyncio

from graph.infra.services.base import BaseService

from .probes.registry import probe_registry


class MetricScheduler(BaseService):
    """
    Manages a background task that periodically executes all probes
    currently active in the central ProbeRegistry.
    """

    def __init__(self, collection_interval_seconds: int):
        super().__init__(service_name="metric_scheduler")
        self._interval = collection_interval_seconds

    async def _run_loop(self) -> None:
        """The main loop that executes the metric probes found in the registry."""
        await self.set_ready()

        while self.is_running():
            try:
                active_probes = probe_registry.all().items()

                self.logger.debug(
                    f"Running collection cycle for {len(active_probes)} probe(s)..."
                )
                for name, probe in active_probes:
                    try:
                        self.logger.debug(
                            f"Executing probe '{name}' ({probe.__class__.__name__})"
                        )
                        await probe.update()
                    except Exception:
                        self.logger.exception(
                            f"Error executing probe '{name}' ({probe.__class__.__name__})"
                        )

                await asyncio.sleep(self._interval)
            except asyncio.CancelledError:
                self.logger.info("MetricScheduler loop cancelled.")
                raise
            except Exception:
                self.logger.exception(
                    "Unexpected error in metric collection loop. Restarting cycle."
                )
                await asyncio.sleep(self._interval)
