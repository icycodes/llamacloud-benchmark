# Create and Query a LlamaCloud Managed Index (Python)

## Background
LlamaCloud provides a managed RAG service that handles document ingestion, embedding, and vector storage in the cloud. You will build a small Python program that ingests a local corpus into a brand-new LlamaCloud managed index and then retrieves relevant context for a question using that index.

The task workspace `/home/user/index_task` already contains a small text corpus in `/home/user/index_task/data` with two pre-seeded files describing a fictional country called Atlantis.

## Requirements
- Read the current `trial_id` from `/logs/artifacts/trial_id`.
- Build a Python script `build_index.py` in `/home/user/index_task` that:
  - Authenticates against LlamaCloud using the `LLAMA_CLOUD_API_KEY` environment variable.
  - Loads the local corpus from `/home/user/index_task/data` using LlamaIndex's `SimpleDirectoryReader`.
  - Creates a new LlamaCloud managed index whose name is `harbor-managed-index-${trial_id}` (the literal base name `harbor-managed-index-` followed by the value read from `/logs/artifacts/trial_id`) inside the `Default` project, using the managed embeddings provided by LlamaCloud (no separate OpenAI key is required).
  - Uses the LlamaCloud index as a retriever to fetch nodes relevant to the query string `What is the capital of Atlantis?`.
  - Writes the retrieval result to a log file `/home/user/index_task/output.log` so a downstream verifier can confirm the retrieval worked.
- The script must run end-to-end with `python3 build_index.py` and exit with status `0`.

## Implementation Hints
- Install package `llama-index-indices-managed-llama-cloud` exposes `from llama_index.indices.managed.llama_cloud import LlamaCloudIndex` (already pre-installed in the environment).
- `LlamaCloudIndex.from_documents(documents, name, project_name="Default")` will both create the managed pipeline on LlamaCloud and ingest the documents. It blocks until ingestion is complete when called synchronously; using `verbose=True` is helpful while debugging.
- `index.as_retriever()` returns a retriever you can call with `.retrieve("<your question>")` to obtain a list of `NodeWithScore` items. Use the joined `node.get_content()` (or `.text`) of those items as the retrieval result string.
- Make sure to read `trial_id` from `/logs/artifacts/trial_id` and append it to the index name so concurrent runs do not collide.

## Acceptance Criteria
- Project path: `/home/user/index_task`
- Script path: `/home/user/index_task/build_index.py`
- Log file: `/home/user/index_task/output.log`
- Command: `python3 /home/user/index_task/build_index.py`
  - The command must exit with status code `0`.
- The created LlamaCloud managed index name must be `harbor-managed-index-${trial_id}` where `trial_id` is the value read from `/logs/artifacts/trial_id`, and it must live in the LlamaCloud `Default` project.
- The log file must:
  - Be a non-empty UTF-8 text file.
  - Contain a line of the form `Index name: harbor-managed-index-<trial_id>` so the verifier can confirm the resource name.
  - Contain a section that prints the retrieved context returned by the LlamaCloud retriever for the query `What is the capital of Atlantis?`. The retrieved context must include the textual answer for the capital of Atlantis present in the seeded corpus.

