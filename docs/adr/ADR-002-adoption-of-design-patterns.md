# ADR-002: Adoption of Design Patterns

* **Status:** Proposed
* **Date:** 2025-08-31

## Context

The RAG system is a critical component that needs to be scalable, reliable, and maintainable in a production environment. The initial starter kit provides a simple, monolithic structure that tightly couples business logic with concrete technology implementations. This approach makes it difficult to:
* Swap out a database (e.g., Weaviate for Milvus).
* Add cross-cutting concerns like logging, metrics, and tracing in a consistent manner.
* Manage the application lifecycle (startup/shutdown) cleanly.
* Implement advanced resilience patterns like retries and circuit breakers.

We need a structured architectural pattern that addresses these challenges without adding unnecessary complexity.

## Decision

We will refactor the project using a set of engineering principles inspired by a personal project, referred to as the "Fortify" pattern, . This pattern dictates the use of the following core concepts:

1.  **Protocol-Oriented Programming**: Define clear interfaces (`Protocols`) for all external dependencies and core components (e.g., `VectorStoreProtocol`, `GraphStoreProtocol`).
2.  **Dependency Injection via Factories**: Implement `Factory` classes (`VectorStoreFactory`, `GraphStoreFactory`) that are responsible for instantiating concrete implementations based on the application's configuration. This centralizes the choice of technology.
3.  **Managed Service Lifecycle**: All stateful components (databases, caches, etc.) will inherit from a `BaseService` class, which provides a standard `start()`/`stop()` lifecycle. An orchestrator, the `LifecycleManager`, will manage the startup and shutdown of all services in a defined order of priority.

This pattern will be applied to all layers of the RAG system, from the data ingestion pipelines to the query API.

`(IMPORTANT: This is not a new design pattern, it's just the consistent use of them.)`

## Consequences

* **Positive:**
    * **High Maintainability and Testability:** The clear separation of concerns makes it easy to write unit tests with mock implementations of the `Protocols`.
    * **Flexibility and Vendor Agnosticism:** We can easily switch underlying technologies (e.g., change from Weaviate to Pinecone) by implementing a new class that adheres to the same `Protocol` and updating the configuration.
    * **Production Readiness:** The built-in support for observability (metrics/tracing) and a standardized lifecycle makes the system inherently more stable and easier to operate in production.

* **Negative:**
    * **Increased Initial Overhead:** Setting up the `Protocols`, `Factories`, and the `BaseService` hierarchy requires more upfront architectural work than a monolithic approach.
    * **Learning Curve:** New developers joining the project will need to understand the architectural patterns and abstractions before being fully productive.

* **Neutral/Other:**
    * **Code Naming:** The use of terms like "Fortify" and "graph" will be kept internal to the project's infrastructure layer to avoid confusion with domain-specific logic.