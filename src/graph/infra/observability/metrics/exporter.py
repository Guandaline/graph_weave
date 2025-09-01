from loguru import logger
from prometheus_client import start_http_server

from graph.infra.config import get_settings


def start_metrics_server() -> None:
    settings = get_settings().observability

    if settings.enabled:
        port = settings.exporter_port
        logger.info(f"Starting metrics server on port {port}")
        start_http_server(port)
    else:
        logger.info("Observability is disabled via settings.")
