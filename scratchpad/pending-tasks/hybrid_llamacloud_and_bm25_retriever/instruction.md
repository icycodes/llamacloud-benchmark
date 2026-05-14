Relying purely on vector similarity can sometimes miss exact keyword matches. Combining LlamaCloud's managed retrieval with a local keyword-based search provides a robust hybrid retrieval mechanism.

You need to implement a custom retriever class `HybridCloudRetriever` in a file named `hybrid.py`. This class must accept an instantiated `LlamaCloudIndex` retriever and a local LlamaIndex `BM25Retriever`. Its `_retrieve` method should query both retrievers concurrently (or sequentially) for a given query string, combine the results, deduplicate them based on node IDs, and return the final list.

**Constraints:**
- Must inherit from LlamaIndex's `BaseRetriever`.
- Must return a list of standard LlamaIndex `NodeWithScore` objects.
- Deduplication logic must prioritize the score from the LlamaCloud retriever if a node appears in both sets.