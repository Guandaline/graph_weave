# ADR-003: Selection of Vector and Graph Databases

* **Status:** Proposed
* **Date:** 2025-08-31

## Context

To implement the hybrid RAG architecture (ADR-001), we need to select specific database technologies for storing and retrieving vector embeddings and graph data. The solution must be performant, scalable, and compatible with the "Fortify" architectural pattern (ADR-002).

We considered the following options:
* **Vector Databases**: Weaviate, Pinecone, Milvus, Qdrant.
* **Graph Databases**: Neo4j, JanusGraph, ArangoDB.

Constraints include ease of setup via `docker-compose.yml`, Python client library maturity, and community support.

## Decision

We will use **Weaviate** as our primary vector database and **Neo4j** as our primary graph database. The `docker-compose.yml` file from the starter kit will serve as the foundation for our infrastructure setup.

* **Weaviate**: It offers a built-in HNSW index, which provides a good balance of search performance (latency) and recall, with a straightforward Python client library.
* **Neo4j**: It is the industry standard for graph databases, optimized for graph traversal (which is a core requirement for our hybrid approach) and provides a powerful query language (Cypher).

Both technologies have mature Python clients and are easily "containered", aligning with our MLOps and reliability requirements. We will configure both to run locally in a single `docker compose` file.

## Consequences

* **Positive:**
    * **Strong Performance:** The combination is well-suited for the hybrid approach, with Weaviate handling semantic search and Neo4j excelling at relational queries.
    * **Ease of Integration:** The Python client libraries for both are well-documented and robust, simplifying the development of our `VectorStoreProtocol` and `GraphStoreProtocol` implementations.
    * **Clear Development Path:** The starter kit provides a solid foundation, allowing us to focus on implementing the core logic rather than spending time on infrastructure setup.

* **Negative:**
    * **Vendor Lock-in Risk:** While our architecture pattern mitigates this, relying on proprietary technologies can make future migrations to open-source alternatives (like Milvus or JanusGraph) more complex.
    * **Resource Consumption:** Both databases can be memory and CPU-intensive, especially at scale. We will need to carefully monitor resource usage and apply sharding strategies as outlined in our scaling plan.

* **Neutral/Other:**
    * **Alternative Backends:** The use of the "Fortify" `Protocol` pattern leaves the door open for easily implementing and swapping in alternative backends in the future, if business needs change. For instance, a community member could contribute a Milvus implementation for the `VectorStoreProtocol`.