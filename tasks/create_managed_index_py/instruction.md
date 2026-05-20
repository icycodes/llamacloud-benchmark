# Create a LlamaCloud Managed Index in Python

## Background
LlamaCloud is LlamaIndex's managed service for production-grade RAG. Instead of running your own vector store, you push your documents to LlamaCloud and let it handle parsing, embedding, indexing, and retrieval. In this task you will write a Python program that ingests a small corpus of local text documents into a new LlamaCloud managed index and then performs a retrieval query against it.

The task environment contains three small plain-text documents under `/home/user/myproject/data/` (one each about cats, dogs, and birds). Your program must build a LlamaCloud managed index from those documents, perform a retrieval, and record the results in a log file.

## Requirements
- Read the `trial_id` from `/logs/artifacts/trial_id` and use it to derive a unique LlamaCloud index name.
- Create a brand-new LlamaCloud managed index in the `default` project that contains all three of the provided documents.
- Wait for ingestion to complete so that retrieval is possible.
- Use the LlamaCloud index's retriever to retrieve the top-3 most relevant nodes for the query `What do cats like to eat?`.
- Write the index name, the number of nodes retrieved, and the text content of every retrieved node to a log file.
- The same script must be runnable as a one-off command and must not depend on any pre-existing index with the same name.

## Implementation Hints
- Install and use the `llama-index-indices-managed-llama-cloud` Python package (the `LlamaCloudIndex` class) together with `llama-index-core` (for `SimpleDirectoryReader`).
- The LlamaCloud API key is provided via the `LLAMA_CLOUD_API_KEY` environment variable.
- `LlamaCloudIndex.from_documents(...)` accepts `name`, `project_name`, `verbose`, and similar arguments and will create the managed index.
- The retriever returned by `index.as_retriever(...)` exposes a `.retrieve(query_str)` method and returns a list of `NodeWithScore` objects whose text is accessible via `node.get_content()` or `node.text`.
- You do not need an LLM or an `OPENAI_API_KEY` for retrieval; LlamaCloud handles embeddings server-side with its managed defaults.

## Acceptance Criteria
- Project path: `/home/user/myproject`
- Log file: `/home/user/myproject/output.log`
- The program must create a new LlamaCloud managed index whose name is exactly `harbor-managed-index-${trial_id}`, where `trial_id` is read from `/logs/artifacts/trial_id`. The index must live in the LlamaCloud project named `default`.
- The newly created managed index must contain ingested content from all three files in `/home/user/myproject/data/` (`cats.txt`, `dogs.txt`, `birds.txt`).
- The log file must contain:
  - A line in the form: `Index name: harbor-managed-index-<trial_id>`
  - A line in the form: `Retrieved nodes: <N>` where `<N>` is an integer greater than or equal to 1.
  - The full text of every retrieved node, each printed on its own line prefixed with `Node text: `.
- The retrieval query used must be `What do cats like to eat?` and at least one logged `Node text:` line must contain the substring `cat` (case-insensitive).

