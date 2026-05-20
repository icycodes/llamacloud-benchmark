# Create and Query a LlamaCloud Managed Index (TypeScript)

## Background
LlamaCloud is a managed RAG-as-a-Service platform from LlamaIndex. In this task you will use the TypeScript SDK (the `llamaindex` package) to spin up a new managed index, ingest a small set of local text documents into it, and execute a natural-language query against the resulting index using its query engine.

The project skeleton has been prepared for you at `/home/user/myproject`:
- `data/` — contains plain-text source documents that must be ingested into the managed index.
- `package.json` — already declares the `llamaindex` dependency and a `start` script that runs `index.ts` via `tsx`.
- `tsconfig.json` — ready-to-use TypeScript config.

Dependencies (including `llamaindex` and `tsx`) are already installed under `node_modules/`.

## Requirements
- Implement a Node.js/TypeScript program at `/home/user/myproject/index.ts` that:
  1. Reads the current `trial_id` from `/logs/artifacts/trial_id` and uses it to build a unique index name `harbor-ts-index-${trial_id}` (so concurrent trials never collide on a shared name).
  2. Loads the documents under `/home/user/myproject/data` (a `SimpleDirectoryReader` works well).
  3. Creates a new LlamaCloud managed index from those documents using `LlamaCloudIndex.fromDocuments`, in the `Default` project. The `LLAMA_CLOUD_API_KEY` env var is already exported.
  4. Builds a query engine from the index and asks the question: `What is the capital of France?`.
  5. Writes the answer and a small JSON summary to `/home/user/myproject/output.log` using the format described below.
- The program must be runnable from the project directory with `npm start` and must exit with code 0 on success.

## Implementation Hints
- Import `LlamaCloudIndex` and `SimpleDirectoryReader` from the `llamaindex` package.
- `LlamaCloudIndex.fromDocuments` is asynchronous and accepts at minimum `{ documents, name, projectName }`. The Default project is named `Default`.
- The query engine is created with `index.asQueryEngine()` and queried with `await queryEngine.query({ query: '...' })`. The textual response is on the `.message.content` (or `.response`) field — print whatever string representation the SDK returns.
- Read the trial id with the standard `node:fs` API; do not hard-code a name.
- Make sure the script writes the log file before exiting so the verifier can read it.

## Acceptance Criteria
- Project path: /home/user/myproject
- Source file: /home/user/myproject/index.ts
- Start command: npm start (executed from /home/user/myproject)
- Log file: /home/user/myproject/output.log
- The program reads `trial_id` from `/logs/artifacts/trial_id` and creates exactly one new LlamaCloud managed index in the `Default` project named `harbor-ts-index-${trial_id}`.
- All documents from `/home/user/myproject/data` are ingested into that index.
- The query engine is invoked at least once on the created index.
- `output.log` must contain, in this order:
  - A line starting with `Index name: harbor-ts-index-<trial_id>`.
  - A line starting with `Query: What is the capital of France?`.
  - A line starting with `Answer: ` followed by the model's natural-language response (a non-empty string).
  - A final JSON line starting with `Summary: ` followed by a JSON object containing at least the keys `index_name` (string equal to `harbor-ts-index-<trial_id>`) and `num_documents` (integer equal to the number of files ingested from `data/`).

