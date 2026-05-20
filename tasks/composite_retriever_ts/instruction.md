# Composite Retriever across Multiple LlamaCloud Indices (TypeScript)

## Background
LlamaCloud is a managed RAG-as-a-Service platform from LlamaIndex. In real applications, different document types (e.g. company policies vs. product FAQs) benefit from being stored in separate managed indices so each can use its own parsing and chunking configuration. The LlamaCloud Client SDK (`@llamaindex/llama-cloud`) exposes a Composite Retriever that fans out a single query across multiple indices and globally re-ranks the results.

Your task is to build a small TypeScript program that programmatically creates two managed indices, ingests local files into each one, wires them together with a Composite Retriever, and runs a query that returns hits drawn from both indices.

## Requirements
- The program must be implemented in TypeScript and executed with `tsx`.
- Use the `@llamaindex/llama-cloud` Client SDK to:
  - Create (upsert) two separate managed pipelines (indices) — one for "policies" content and one for "faq" content.
  - Upload the local input files into the correct pipeline.
  - Wait until both pipelines finish ingestion.
  - Create a Composite Retriever that references both pipelines.
  - Run a query against the Composite Retriever in `full` mode and capture the returned nodes.
- All externally visible resource names (pipelines and retriever) must be scoped with the current `trial_id` so concurrent runs do not collide.
- Write a structured log file that summarizes the created resources and the query result.

## Implementation Hints
- Read the current `trial_id` from `/logs/artifacts/trial_id` (a single-line file). Trim whitespace before using it.
- The two pipelines must be named exactly:
  - `policies-${trial_id}` — ingest the files under `./data/policies`
  - `faq-${trial_id}` — ingest the files under `./data/faq`
- Use `client.pipelines.upsert(...)` to create or update each pipeline. For embeddings, configure `OPENAI_EMBEDDING` with `text-embedding-3-small` and the API key from the `OPENAI_API_KEY` environment variable. Use the managed data sink (`data_sink_id: null`).
- Upload local files with `client.files.create({ file: fs.createReadStream(...), purpose: "user_data" })`, then attach them to a pipeline using `client.pipelines.files.create(pipelineId, { body: [...] })`.
- Poll `client.pipelines.getStatus(pipelineId)` until ingestion leaves the `NOT_STARTED` / `IN_PROGRESS` states for both pipelines before retrieval.
- Create the composite retriever via `client.retrievers.create({ name: "composite-retriever-${trial_id}", pipelines: [...] })`. Give each sub-pipeline a meaningful `description` so the routing agent could disambiguate them.
- Query with `client.retrievers.retriever.search(retrieverId, { query, mode: "full", rerank_top_n: 5 })`.
- The `LLAMA_CLOUD_API_KEY` and `OPENAI_API_KEY` environment variables are already set in the runtime.

## Acceptance Criteria
- Project path: /home/user/composite_retriever
- Log file: /home/user/composite_retriever/output.log
- The program is run with `npx tsx index.ts` from the project path and must exit with status 0.
- The `trial_id` is read from `/logs/artifacts/trial_id`.
- Two LlamaCloud pipelines named `policies-${trial_id}` and `faq-${trial_id}` exist in the configured LlamaCloud project after the run.
- A LlamaCloud retriever named `composite-retriever-${trial_id}` exists and references both pipelines.
- The log file must contain the following lines, in any order, with literal prefixes (case-sensitive):
  - `Trial ID: <trial_id>`
  - `Policies Pipeline ID: <pipeline_id>`
  - `FAQ Pipeline ID: <pipeline_id>`
  - `Composite Retriever ID: <retriever_id>`
  - `Query: <query string>`
  - `Result Count: <n>` where `<n>` is the integer number of retrieved nodes (must be >= 1)
  - At least one line per retrieved node in the format `Node Score: <score> | Text: <first 80 chars of text>`

