"""List of useful metrics."""

from prometheus_client import CollectorRegistry, Counter, Histogram

registry = CollectorRegistry()

# Prometheus metrics
REQUEST_COUNT = Counter(
    "api_requests_total",
    "Total number of API requests",
    ["api_name"],
    registry=registry,
)

REQUEST_LATENCY = Histogram(
    "api_request_latency_seconds",
    "Latency of API requests",
    ["api_name"],
    registry=registry,
)
