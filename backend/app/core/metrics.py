from prometheus_client import Counter, Histogram

# Gemini metrics explicitly matching structural constraints inherently
gemini_requests_total = Counter(
    "gemini_requests_total",
    "Total LLM generation iterations executed externally successfully",
    ["status"]
)

gemini_request_latency_seconds = Histogram(
    "gemini_request_latency_seconds",
    "LLM latency timings smoothly structurally",
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0]
)

# Qdrant metrics safely securely mapping natively internal states
qdrant_requests_total = Counter(
    "qdrant_requests_total",
    "Total targeted Vector Search interactions cleanly processed",
    ["status"]
)

qdrant_query_latency_seconds = Histogram(
    "qdrant_query_latency_seconds",
    "Query execution bindings tracked precisely structurally",
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0]
)

# Reranker metrics cleanly mapping execution failures gracefully inherently  
reranker_requests_total = Counter(
    "reranker_requests_total",
    "Reranker filtering pipeline hits internally handled securely",
    ["fallback_triggered"]
)

reranker_latency_seconds = Histogram(
    "reranker_latency_seconds",
    "Reranker computation tracking accurately locally mappings natively",
    buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0]
)

# Ingestion metric limits structurally encoding failures appropriately 
ingestion_jobs_total = Counter(
    "ingestion_jobs_total",
    "Background PDF structuring task pipelines handled correctly structurally",
    ["status"]
)
