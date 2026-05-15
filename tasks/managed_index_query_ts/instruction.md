# Create and Query a LlamaCloud Managed Index (TypeScript)

## Background
LlamaCloud provides a managed RAG service that handles document ingestion, embedding, and vector storage in the cloud. In this task you will build a small TypeScript program that ingests a local corpus into a brand-new LlamaCloud managed index and then retrieves relevant context for a question using that index, using the official LlamaCloud TypeScript framework (`llama-cloud-services`).

The task workspace `/home/user/index_task_ts` already contains a small text corpus in `/home/user/index_task_ts/data` with two pre-seeded files describing a fictional country called Atlantis.

## Requirements
- Read the current `trial_id` from `/logs/artifacts/trial_id`.
- Build a TypeScript script `build_index.ts` in `/home/user/index_task_ts` that:
  - Authenticates against LlamaCloud using the `LLAMA_CLOUD_API_KEY` environment variable.
  - Loads the local corpus from `/home/user/index_task_ts/data` (the seeded `facts.txt` and `history.txt`) and turns the file contents into `Document` objects.
  - Creates a new LlamaCloud managed index whose name is `harbor-managed-index-ts-${trial_id}` (the literal base name `harbor-managed-index-ts-` followed by the value read from `/logs/artifacts/trial_id`) inside the `Default` project, using the managed embeddings provided by LlamaCloud (no separate OpenAI key is required).
  - Uses the LlamaCloud index as a retriever to fetch nodes relevant to the query string `What is the capital of Atlantis?`.
  - Writes the retrieval result to a log file `/home/user/index_task_ts/output.log` so a downstream verifier can confirm the retrieval worked.
- The script must run end-to-end with `npx tsx build_index.ts` from `/home/user/index_task_ts` and exit with status code `0`.

## Implementation Hints
- The TypeScript managed-index integration lives in the `llama-cloud-services` npm package and the `Document` class comes from `llamaindex`. Both packages are already globally installed and resolvable from the project directory (via `NODE_PATH`).
- Use `LlamaCloudIndex.fromDocuments({ documents, name, projectName: "Default", apiKey: process.env.LLAMA_CLOUD_API_KEY })` to create the managed pipeline and ingest the documents in a single call. Setting `verbose: true` is helpful while debugging.
- `index.asRetriever()` returns a retriever. Call `await retriever.retrieve({ query: "<your question>" })` to get a list of `NodeWithScore` items; concatenate each node's text (via `node.node.getContent({ MetadataMode: ... })` or `node.node.text`) to build the retrieval result string for the log.
- Read `trial_id` from `/logs/artifacts/trial_id` and append it to the index name so concurrent runs do not collide.
- `tsx` is preinstalled globally so the script can be executed with `npx tsx build_index.ts` directly.

## Acceptance Criteria
- Project path: `/home/user/index_task_ts`
- Script path: `/home/user/index_task_ts/build_index.ts`
- Log file: `/home/user/index_task_ts/output.log`
- Command: `npx tsx build_index.ts` (run from `/home/user/index_task_ts`).
  - The command must exit with status code `0`.
- LlamaCloud usage:
  - `build_index.ts` must import from the `llama-cloud-services` TypeScript package (e.g. the literal substring `llama-cloud-services`).
- The created LlamaCloud managed index name must be `harbor-managed-index-ts-${trial_id}` where `trial_id` is the value read from `/logs/artifacts/trial_id`, and it must live in the LlamaCloud `Default` project.
- The log file must:
  - Be a non-empty UTF-8 text file.
  - Contain a line of the form `Index name: harbor-managed-index-ts-<trial_id>` so the verifier can confirm the resource name.
  - Contain a section that prints the retrieved context returned by the LlamaCloud retriever for the query `What is the capital of Atlantis?`. The retrieved context must include the textual answer for the capital of Atlantis present in the seeded corpus.

