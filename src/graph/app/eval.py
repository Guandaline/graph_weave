# eval.py

import asyncio
import json
import time
from typing import Any, Dict, List

import httpx
import numpy as np

# --- Configuration ---
API_URL = "http://localhost:8000/query"
GOLD_QUERIES_PATH = "data/gold_queries.jsonl"
CONCURRENT_REQUESTS = 10  # Number of parallel requests to send

# --- Helper Functions ---


async def run_single_query(
    client: httpx.AsyncClient, query_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Sends a single query to the API and measures performance and quality."""
    query_text = query_data["query"]
    gold_doc_id = query_data["doc_id"]

    start_time = time.perf_counter()
    try:
        response = await client.post(API_URL, json={"query": query_text}, timeout=30.0)
        response.raise_for_status()
        latency = time.perf_counter() - start_time

        response_data = response.json()
        returned_doc_ids = {
            cite["doc_id"] for cite in response_data.get("citations", [])
        }

        hit = 1 if gold_doc_id in returned_doc_ids else 0

        return {"latency": latency, "hit": hit, "error": None}

    except httpx.HTTPStatusError as e:
        latency = time.perf_counter() - start_time
        return {
            "latency": latency,
            "hit": 0,
            "error": f"HTTP Error: {e.response.status_code}",
        }
    except Exception as e:
        latency = time.perf_counter() - start_time
        return {"latency": latency, "hit": 0, "error": str(e)}


def load_queries(path: str) -> List[Dict[str, Any]]:
    """Loads queries from a jsonl file."""
    with open(path, "r") as f:
        return [json.loads(line) for line in f]


# --- Main Evaluation Logic ---


async def main():
    """Main function to run the evaluation harness."""
    print("--- Starting RAG System Evaluation ---")

    try:
        queries = load_queries(GOLD_QUERIES_PATH)
    except FileNotFoundError:
        print(f"Error: Gold queries file not found at '{GOLD_QUERIES_PATH}'.")
        print("Please generate the data first using 'python app/generate_data.py'")
        return

    total_queries = len(queries)
    print(f"Found {total_queries} queries to evaluate.")

    latencies: List[float] = []
    hits: int = 0
    errors: int = 0

    semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)

    async with httpx.AsyncClient() as client:
        tasks = []
        for query_data in queries:

            async def limited_query(q_data):
                async with semaphore:
                    return await run_single_query(client, q_data)

            tasks.append(limited_query(query_data))

        results = await asyncio.gather(*tasks)

    for res in results:
        if res["error"] is None:
            latencies.append(res["latency"])
            hits += res["hit"]
        else:
            errors += 1

    # --- Report Results ---
    print("\n--- Evaluation Results ---")

    # Performance Metrics
    if latencies:
        p50_latency = np.percentile(latencies, 50) * 1000  # in ms
        p95_latency = np.percentile(latencies, 95) * 1000  # in ms
        avg_latency = np.mean(latencies) * 1000  # in ms

        print("\n[Performance Metrics]")
        print(f"  - Average Latency: {avg_latency:.2f} ms")
        print(f"  - P50 Latency (Median): {p50_latency:.2f} ms")
        print(f"  - P95 Latency: {p95_latency:.2f} ms")
        print(f"  - Successful Queries: {len(latencies)}/{total_queries}")
        print(f"  - Errors: {errors}")
    else:
        print("\n[Performance Metrics]")
        print("  - No successful queries to report latency.")

    # Quality Metrics
    if total_queries > 0:
        recall_at_k = (hits / total_queries) * 100
        print("\n[Quality Metrics]")
        print(
            f"  - Recall@k: {recall_at_k:.2f}% ({hits}/{total_queries} correct documents retrieved)"
        )

    print("\n--- Evaluation Complete ---")
    print(
        "Note: For per-stage latency breakdown (vector, graph, rerank), please check your tracing backend (e.g., Jaeger)."
    )


if __name__ == "__main__":
    asyncio.run(main())
