# Manage Documents in a LlamaCloud Managed Index: Delete by `ref_doc_id` (Python)

## Background
A real-world LlamaCloud RAG pipeline must support document lifecycle management: documents are added when they become relevant and removed once they are obsolete, sensitive, or simply wrong. In this task you must build a Python program that creates a brand-new LlamaCloud managed index from three local text documents that each have an explicit `id_`, then removes one specific document from the existing managed index using its `ref_doc_id`, and finally proves through retrieval that the deleted document is no longer reachable from the index while the remaining documents still are.

The task workspace `/home/user/delete_task` is pre-seeded with three text files in `/home/user/delete_task/data`:
- `history.txt` — Atlantean history facts (must be assigned `ref_doc_id` `atlantis-history`).
- `cuisine.txt` — Atlantean cuisine facts (must be assigned `ref_doc_id` `atlantis-cuisine`).
- `secret.txt` — A note about a fictional secret artifact called the Lumina Sphere (must be assigned `ref_doc_id` `atlantis-secret`).

## Requirements
- Read the current `trial_id` from `/logs/artifacts/trial_id`.
- Build a Python script `manage_index.py` in `/home/user/delete_task` that:
  - Authenticates against LlamaCloud using the `LLAMA_CLOUD_API_KEY` environment variable.
  - Constructs **three** `llama_index.core.Document` objects from the three seeded files, assigning each document the explicit `id_` listed above (`atlantis-history`, `atlantis-cuisine`, `atlantis-secret`). The text content of each document must be the contents of the corresponding seed file.
  - Creates a brand-new LlamaCloud managed index whose name is `harbor-delete-index-${trial_id}` (the literal base name `harbor-delete-index-` followed by the value read from `/logs/artifacts/trial_id`) inside the `Default` project, populated with all three documents.
  - After the index exists and is fully ingested, deletes the document whose `ref_doc_id` is `atlantis-secret` from the same managed index using `LlamaCloudIndex.delete_ref_doc(...)`. The pipeline itself must remain — only that one document is removed.
  - Uses the updated index as a retriever (with a reasonably high top-k such as `5`) to fetch nodes for the query `What is the Lumina Sphere of Atlantis?` and writes the retrieved context into the log so the verifier can confirm the deletion took effect.
  - Uses the updated index as a retriever to fetch nodes for the query `What is the national dish of Atlantis?` and writes the retrieved context into the log so the verifier can confirm the remaining documents are still searchable.
  - Writes a log file `/home/user/delete_task/output.log` summarizing the workflow.
- The script must run end-to-end with `python3 manage_index.py` and exit with status code `0`.

## Implementation Hints
- The managed-index integration is `llama_index.indices.managed.llama_cloud.LlamaCloudIndex` (already pre-installed). `LlamaCloudIndex.from_documents(documents, name=..., project_name="Default")` will create the managed pipeline and ingest the documents synchronously; passing `verbose=True` is helpful while debugging.
- Construct `Document` objects directly so you can assign explicit IDs, e.g. `Document(text=open(...).read(), id_="atlantis-secret")`. The same `id_` value is the `ref_doc_id` used by deletion APIs.
- `LlamaCloudIndex.delete_ref_doc(ref_doc_id, verbose=True)` deletes a single document by its `ref_doc_id` and internally waits for the managed pipeline to finish processing the deletion before returning, so retrieval performed after the call should already reflect the change.
- `index.as_retriever(similarity_top_k=5)` returns a retriever; calling `.retrieve("<question>")` returns a list of `NodeWithScore` items whose `.get_content()` (or `.text`) attribute holds the retrieved text. Log the joined content so the verifier can search it.
- Append `trial_id` to the index name so parallel trials do not collide. Read it once from `/logs/artifacts/trial_id` and reuse it everywhere.

## Acceptance Criteria
- Project path: `/home/user/delete_task`
- Script path: `/home/user/delete_task/manage_index.py`
- Log file: `/home/user/delete_task/output.log`
- Command: `python3 /home/user/delete_task/manage_index.py`
  - The command must exit with status code `0`.
- The created LlamaCloud managed index name must be `harbor-delete-index-${trial_id}` where `trial_id` is the value read from `/logs/artifacts/trial_id`, and it must live in the LlamaCloud `Default` project.
- The log file must:
  - Be a non-empty UTF-8 text file.
  - Contain a line of the form `Index name: harbor-delete-index-<trial_id>` so the verifier can confirm the resource name.
  - Contain a line of the form `Deleted document id: atlantis-secret` so the verifier can confirm which `ref_doc_id` was removed.
  - Contain a section that prints the retrieved context returned by the retriever for the query `What is the Lumina Sphere of Atlantis?`. This retrieved context **must not** contain the case-insensitive phrase `Lumina Sphere` (because the document that mentioned it was deleted).
  - Contain a section that prints the retrieved context returned by the retriever for the query `What is the national dish of Atlantis?`. This retrieved context **must** contain a recognizable phrase from `cuisine.txt` (specifically the case-insensitive phrase `grilled seaweed`) to prove the remaining documents are still searchable.

