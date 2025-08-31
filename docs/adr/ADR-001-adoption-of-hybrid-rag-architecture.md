# ADR-087: Adoption of Hybrid RAG Architecture

* **Status:** Proposed
* **Date:** 2025-08-31

## Context

The objective is to build a high-quality RAG system that is reliable, scalable, and provides rich, contextual answers. A naive approach using only dense retrieval (vector search) often falls short in answering complex questions that require understanding relationships between entities. For example, "What products did a specific customer buy from a specific brand in the last year?". This requires navigating structured relationships that are poorly represented by vector embeddings alone.

We considered the following alternatives:
* **Pure Dense Retrieval**: Simple to implement, but lacks the ability to understand entity relationships, leading to poor quality for complex queries.
* **Hybrid RAG with Text-only Graph**: Indexing relationships as plain text in the vector store. This is a hacky solution that can work for simple cases but quickly becomes unscalable and imprecise as the graph size and complexity grow.

## Decision

We will implement a hybrid RAG architecture that combines two retrieval methods:
1.  **Dense Retrieval (Vector Search)**: For semantic similarity, finding the most relevant documents based on the query's meaning. We will use a vector database for this.
2.  **Graph Traversal (Entity/Relationship Expansion)**: To enrich the context by following explicit relationships between entities mentioned in the top-k documents from the vector search. We will use a graph database for this.

The final context will be a fusion of results from both sources, followed by a re-ranking step to present the most relevant information to the LLM.

## Consequences

* **Positive:**
    * **Improved Query Quality:** The hybrid approach significantly increases the system's ability to handle complex, multi-hop queries that require relational understanding.
    * **Contextual Richness:** By leveraging the graph, we provide a more comprehensive context to the LLM, reducing hallucinations and improving answer accuracy.
    * **Architectural Flexibility:** The clear separation of concerns allows us to independently optimize and scale the vector and graph components.

* **Negative:**
    * **Increased Infrastructure Complexity:** The solution requires managing and orchestrating two different database systems (vector and graph), increasing the operational overhead.
    * **Higher Latency Potential:** Combining results from two systems and performing re-ranking can introduce additional latency compared to a single-source retrieval. This will require careful optimization.
    * **Data Consistency Challenge:** We must ensure that the entities and relationships in the graph are synchronized with the documents in the vector store during ingestion.

* **Neutral/Other:**
    * **Re-ranking Strategy:** The final quality will heavily depend on the effectiveness of our re-ranking function, which will need to be carefully designed and possibly fine-tuned.