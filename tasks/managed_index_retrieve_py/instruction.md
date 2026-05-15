# Build a Managed LlamaCloud Index and Retrieve Nodes

## Background
You are building a small Retrieval-Augmented Generation (RAG) prototype on **LlamaCloud**, the managed RAG-as-a-Service platform from LlamaIndex. Your job is to create a managed `LlamaCloudIndex` from a tiny local document collection, then use that index's **retriever** (not a full LLM-backed query engine) to fetch the most relevant chunk for a specific question. Using the retriever — rather than a query engine — avoids needing a separate LLM API key and exercises the core LlamaCloud managed retrieval path end to end.

The Python SDK `llama-index-indices-managed-llama-cloud` is already installed. The LlamaCloud account is already provisioned, and the API key is available in the environment variable `LLAMA_CLOUD_API_KEY`. The default project name to use is `Default`. A small set of plain-text documents is pre-staged in `/home/user/myproject/docs/` and includes a file describing a fictional internal initiative named **Project Aurora**, whose stated mission is to *catalog every star in the Milky Way*.

Because this task may run multiple times concurrently against the same LlamaCloud project, your managed index name **MUST be unique per trial run**: append the `trial_id` from `/logs/artifacts/trial_id` as a suffix to the base name `harbor-mgr-idx`.

## Requirements
Write a Python script at `/home/user/myproject/build_and_retrieve.py` that:
- Reads the `trial_id` value from `/logs/artifacts/trial_id`.
- Loads every file in `/home/user/myproject/docs/` as a list of LlamaIndex `Document` objects (e.g. via `SimpleDirectoryReader`).
- Creates a **new** managed `LlamaCloudIndex` from those documents using:
  - `name = "harbor-mgr-idx-<trial_id>"` (substituting the actual `trial_id`)
  - `project_name = "Default"`
  - Authentication via the `LLAMA_CLOUD_API_KEY` environment variable
- Waits for indexing to finish so that retrieval is possible (the SDK's `from_documents` constructor handles this synchronously by default).
- Uses the index's retriever (`index.as_retriever(...)`) to retrieve the most relevant nodes for the query:

  > `What is the mission of Project Aurora?`

- Writes a Markdown summary to `/home/user/myproject/output.md` that contains:
  - A top heading `# LlamaCloud Retrieval Result`.
  - The full text of the **top-1** retrieved node (i.e., the node with the highest similarity score) under a sub-heading `## Top Node`.
- Writes a plain-text log to `/home/user/myproject/output.log` that contains at minimum the following three lines (one fact per line):
  - `trial_id: <trial_id>` — the value read from `/logs/artifacts/trial_id`.
  - `index_name: harbor-mgr-idx-<trial_id>` — the exact managed-index name created on LlamaCloud.
  - `num_retrieved: <N>` — where `<N>` is the number of nodes returned by the retriever (a positive integer).

## Implementation Hints
- Import `LlamaCloudIndex` from `llama_index.indices.managed.llama_cloud` and `SimpleDirectoryReader` from `llama_index.core`.
- The SDK reads `LLAMA_CLOUD_API_KEY` automatically from the environment; you can also pass `api_key=...` explicitly if you prefer.
- The base name for the index is fixed (`harbor-mgr-idx`); only the trial-id suffix changes per run. The full name **must** equal `harbor-mgr-idx-<trial_id>`.
- `index.as_retriever()` returns a retriever whose `.retrieve(query)` method yields a list of `NodeWithScore` objects; each has `.node.get_content()` (or `.node.text`) and `.score` attributes.
- The script must run end to end with `python3 build_and_retrieve.py` from `/home/user/myproject` and exit with status code `0`.

## Acceptance Criteria
- Project path: `/home/user/myproject`
- Script path: `/home/user/myproject/build_and_retrieve.py`
- Command: `python3 build_and_retrieve.py` (run from `/home/user/myproject`)
- The script must exit with return code `0`.
- A managed LlamaCloud index named exactly `harbor-mgr-idx-<trial_id>` must exist in project `Default` after the script runs, where `<trial_id>` is the value of `/logs/artifacts/trial_id`.
- Output files created by the script:
  - `/home/user/myproject/output.md` — non-empty Markdown that contains:
    - The heading `# LlamaCloud Retrieval Result`.
    - The sub-heading `## Top Node`.
    - Text that mentions both `Project Aurora` and the phrase `catalog every star in the Milky Way` (case-insensitive matches are acceptable for these phrases).
  - `/home/user/myproject/output.log` — must contain:
    - A line matching `trial_id: <trial_id>` where `<trial_id>` equals the value in `/logs/artifacts/trial_id`.
    - A line matching `index_name: harbor-mgr-idx-<trial_id>`.
    - A line matching `num_retrieved: <N>` where `<N>` is a positive integer (>= 1).

