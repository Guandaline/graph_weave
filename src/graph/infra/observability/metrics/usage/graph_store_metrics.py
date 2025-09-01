from prometheus_client import Counter, Histogram

GRAPH_STORE_LATENCY = Histogram(
    "graph_store_latency_seconds",
    "Latency of graph store operations",
    labelnames=["provider", "operation", "status"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

GRAPH_STORE_OPERATIONS_TOTAL = Counter(
    "graph_store_operations_total",
    "Total number of operations executed on the graph store",
    labelnames=["provider", "operation", "status"],
)
