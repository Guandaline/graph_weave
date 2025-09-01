from prometheus_client import Counter, Histogram

VECTOR_STORE_LATENCY = Histogram(
    "vector_store_latency_seconds",
    "Latency of vector store operations",
    labelnames=["provider", "operation", "status"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

VECTOR_STORE_OPERATIONS_TOTAL = Counter(
    "vector_store_operations_total",
    "Total number of operations executed on the vector store",
    labelnames=["provider", "operation", "status"],
)
