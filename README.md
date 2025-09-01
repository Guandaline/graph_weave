```markdown
# Graph Weave: A Production-Ready Hybrid RAG Architecture

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![imports: ruff](https://img.shields.io/badge/imports-ruff-222222.svg)](https://github.com/astral-sh/ruff)

This project implements a production-minded Retrieval-Augmented Generation (RAG) system that combines dense vector search with graph-based context enrichment. The core focus is on building a scalable, maintainable, and observable system using robust software engineering patterns, rather than solely fine-tuning RAG quality metrics.

---

### A Note on Project Context

This repository represents a foundational slice of a larger, personal application framework. The primary goal here was to prototype and validate a hybrid Graph+Vector RAG architecture using production-grade patterns (observability, dependency injection, lifecycle management).

The advanced RAG evaluation and metric optimization aspects are intentionally separated into a dedicated project to manage complexity. The patterns and services validated here are intended to be merged back into the main framework upon completion.

---

## ✨ Core Philosophy

The system is built upon a set of engineering principles inspired by the "Fortify" pattern, which prioritizes production readiness from day one. The key architectural decisions are documented in the [Architectural Decision Records (ADRs)](./docs/adr/).

- **Protocol-Oriented & Vendor Agnostic** : Core components like data stores are defined by abstract protocols (`GraphStoreProtocol`, `VectorStoreProtocol`). This decouples the business logic from concrete implementations (e.g., Neo4j, Weaviate), making it easy to swap technologies without major refactoring.
- **Managed Service Lifecycle** : All stateful services (databases, caches, etc.) adhere to a `BaseService` contract with `start()` and `stop()` methods. A central `lifespan` manager orchestrates the application startup and shutdown gracefully.
- **Full-Stack Observability**: The system is instrumented for deep visibility out-of-the-box, with distributed tracing, structured logging, and a complete monitoring stack.
- **Developer Experience First**: A streamlined setup and automated quality gates ensure that developers can contribute safely and efficiently.

##  Architectural Overview

The system follows a hybrid retrieval strategy to provide rich, contextual answers for complex queries.

**Query Flow:**

1.  A user query is received by the **FastAPI** endpoint.
2.  The `RetrievalService` embeds the query into a vector.
3.  **Dense Retrieval**: The vector is used to perform a similarity search in **Weaviate** to find the top-k relevant documents.
4.  **Entity Extraction**: Entities are extracted from the retrieved documents.
5.  **Graph Expansion**: These entities are used as seeds to traverse the **Neo4j** graph, discovering related entities and concepts within a configured number of hops.
6.  **Fusion & Re-ranking**: The initial documents are re-ranked, boosting the scores of those related to the expanded graph context.
7.  The enriched and re-ranked context is returned with citations.

For detailed architectural decisions, please see:
* **ADR-001**: [Adoption of Hybrid RAG Architecture](./docs/adr/ADR-001-adoption-of-hybrid-rag-architecture.md) 
* **ADR-002**: [Adoption of Design Patterns](./docs/adr/ADR-002-adoption-of-design-patterns.md) 
* **ADR-003**: [Selection of Vector and Graph Databases](./docs/adr/ADR-003-selection-of-vector-and-graph-databases.md) 

## 🚀 Getting Started

### Prerequisites
* Poetry 
* Docker and Docker Compose 

### 1. Environment Setup
The `setup.sh` script will create a virtual environment, install dependencies, and set up pre-commit hooks.

```bash
# Give execution permission to scripts
chmod +x bin/*.sh

# Run the setup script
./bin/setup.sh
```

### 2. Start Infrastructure
This command starts the Neo4j and Weaviate containers in the background.

```bash
# The '-d' flag runs the containers in detached mode
docker compose -f infra/docker-compose.all.yml up -d
```

### 3. Data Ingestion
Run the ingestion script to populate the databases with synthetic data.

```bash
# Activate the virtual environment
source .venv/bin/activate

# Run the ingestion pipeline
python -m src.graph.ingestion.executor
```

### 4. Run the API
Start the FastAPI application using Uvicorn.

```bash
uvicorn src.graph.api.main:app --host 0.0.0.0 --port 8000 --reload
```
The API will be available at `http://localhost:8000`.

### 5. Run Evaluation Harness
This script sends a series of predefined queries to the API to calculate baseline performance and quality metrics.

```bash
python -m src.graph.app.eval
```

## 🔭 Observability

The project includes a complete, containerized monitoring stack.

* **Prometheus**: `http://localhost:9090`  (Collects metrics)
* **Grafana**: `http://localhost:3000`  (For dashboards; user/pass: `admin`/`admin`)
* **Alertmanager**: `http://localhost:9093`  (Manages alerts)

To start the monitoring stack:
```bash
docker compose -f monitoring/docker-compose.yml up -d
```

## 📈 Scaling and Production Considerations

The architecture was designed with scalability in mind.

* **Database Scaling**: Both Weaviate and Neo4j are configured to run in Docker but can be swapped for managed, horizontally scalable cloud clusters. The protocol-based design ensures this requires no application code changes.
* **Multi-Tenancy**: The `ExecutionContext` system is the foundation for tenant isolation. It can be used to automatically filter queries and data at the storage layer.
* **Caching**: A distributed cache like Redis could be easily introduced in front of the `RetrievalService` to cache responses for common queries, drastically reducing latency.
* **Stateless API**: The API is stateless, allowing it to be scaled horizontally behind a load balancer.

## 🤝 Contributing

Contributions are welcome! Please read our [CONTRIBUTING.md](./CONTRIBUTING.md) guide to get started.
All interactions with the project are governed by our [Code of Conduct](./CODE_OF_CONDUCT.md).

## 📜 License

This project is licensed under the Apache-2.0 License. See the [LICENSE](https://www.apache.org/licenses/LICENSE-2.0) file for details.
```

>© Guandaline 2025