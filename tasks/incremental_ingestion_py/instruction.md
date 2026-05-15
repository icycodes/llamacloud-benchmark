# Incrementally Ingest Documents into a LlamaCloud Managed Index (Python)

## Background
A real-world LlamaCloud RAG pipeline typically grows over time: a project starts with a small seed corpus, and then new documents are added to the existing managed index as more data becomes available. In this task you must build a Python script that (a) creates a new LlamaCloud managed index from an initial corpus, (b) incrementally inserts additional documents into the same index after it has been created, and (c) retrieves content from the updated index to confirm the new documents are searchable.

The task workspace `/home/user/ingest_task` is pre-seeded with two folders:
- `/home/user/ingest_task/initial_data` — contains the documents that should be used to **create** the managed index.
- `/home/user/ingest_task/extra_data` — contains the documents that must be **inserted later** (after the index already exists).

## Requirements
- Read the current `trial_id` from `/logs/artifacts/trial_id`.
- Build a Python script `ingest.py` in `/home/user/ingest_task` that:
  - Authenticates against LlamaCloud using the `LLAMA_CLOUD_API_KEY` environment variable.
  - Creates a brand-new LlamaCloud managed index whose name is `harbor-incremental-index-${trial_id}` (the literal base name `harbor-incremental-index-` followed by the value read from `/logs/artifacts/trial_id`) inside the `Default` project. The index must be populated **only** from the documents inside `/home/user/ingest_task/initial_data` at creation time.
  - After the index exists, loads the documents in `/home/user/ingest_task/extra_data` and incrementally adds each one to the **same** managed index (i.e. the index from the previous step must not be deleted and re-created — the additional documents must be inserted into the already-created managed index).
  - Uses the updated index to retrieve nodes relevant to the query `What is the Atlantis Aurora?` and confirms that the retrieved context contains content that was added via the incremental insert step.
  - Writes a log file `/home/user/ingest_task/output.log` summarizing what happened so the verifier can confirm both stages of the workflow.
- The script must run end-to-end with `python3 ingest.py` and exit with status code `0`.

## Implementation Hints
- The managed-index integration is `llama_index.indices.managed.llama_cloud.LlamaCloudIndex` (already pre-installed). `LlamaCloudIndex.from_documents(documents, name=..., project_name="Default")` will create the managed pipeline and ingest the documents synchronously; passing `verbose=True` is helpful while debugging.
- For the incremental step, the `LlamaCloudIndex` object exposes an `insert(document)` method that adds a single `llama_index.core.Document` to the existing managed pipeline. Iterate over the extra documents and call `insert` on each one.
- Use `SimpleDirectoryReader` from `llama_index.core` to load both directories, or construct `Document` objects directly from the file text — either approach is fine, but make sure the file names from `extra_data` are preserved in the document metadata so they can be ingested correctly.
- `index.as_retriever()` returns a retriever; calling `.retrieve("<question>")` returns a list of `NodeWithScore` items whose `.get_content()` (or `.text`) attribute holds the retrieved text. Log the joined content so the verifier can search it.
- Append `trial_id` to the index name so parallel trials do not collide. Read it once from `/logs/artifacts/trial_id` and reuse it everywhere.

## Acceptance Criteria
- Project path: `/home/user/ingest_task`
- Script path: `/home/user/ingest_task/ingest.py`
- Log file: `/home/user/ingest_task/output.log`
- Command: `python3 /home/user/ingest_task/ingest.py`
  - The command must exit with status code `0`.
- The created LlamaCloud managed index name must be `harbor-incremental-index-${trial_id}` where `trial_id` is the value read from `/logs/artifacts/trial_id`, and it must live in the LlamaCloud `Default` project.
- The log file must:
  - Be a non-empty UTF-8 text file.
  - Contain a line of the form `Index name: harbor-incremental-index-<trial_id>` so the verifier can confirm the resource name.
  - Contain a line of the form `Inserted documents: <N>` where `<N>` is the integer count of documents that were incrementally added from `/home/user/ingest_task/extra_data` (must be at least 1).
  - Contain a section that prints the retrieved context returned by the retriever for the query `What is the Atlantis Aurora?`. The retrieved context must include text that originated from the incrementally inserted documents (specifically, content about the Atlantis Aurora) so that the verifier can confirm the incremental ingestion actually made the new content searchable.

