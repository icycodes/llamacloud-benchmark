# Build a LlamaCloud Composite Retriever Across Two Managed Indexes (Python)

## Background
You are working in `/home/user/myproject`, which contains two pre-populated document folders:

- `/home/user/myproject/products/` — product specification documents for the fictional Acme Widgets Corporation.
- `/home/user/myproject/support/` — customer support FAQ documents for the same company.

Your job is to build a Python command-line utility that uses the [LlamaIndex managed index integration](https://docs.llamaindex.ai/en/stable/api_reference/indices/llama_cloud/) (the `llama-index-indices-managed-llama-cloud` package) to:

1. Create **two separate** managed indexes on LlamaCloud — one per folder.
2. Combine both indexes into a single `LlamaCloudCompositeRetriever` running in `CompositeRetrievalMode.FULL` mode.
3. Run a natural-language query against the composite retriever and persist the retrieved chunks.

The SDK is already installed in the environment and the `LLAMA_CLOUD_API_KEY` environment variable is configured. You do NOT need to handle authentication explicitly — the SDK reads the API key from the environment automatically.

## Parallel-Run Safety
Many trials may run concurrently and share the same LlamaCloud account, so every external resource you create on LlamaCloud **MUST** be uniquely named. The harness writes the current `trial_id` to the file `/logs/artifacts/trial_id` before the task starts. Read that file and use the value to disambiguate every index and retriever name (see Requirements).

## Requirements
- Implement a Python CLI named `composite.py` at `/home/user/myproject/composite.py`.
- The script must accept exactly four command-line arguments:
  - `--products-dir <path>`: path to the products documents directory.
  - `--support-dir <path>`: path to the support documents directory.
  - `--query <text>`: a natural-language query string.
  - `--output <path>`: the path where the retrieved chunks should be written (UTF-8 text file).
- Read `trial_id` from `/logs/artifacts/trial_id` (the file is a single line). Strip any trailing whitespace/newline.
- Build the resource names using the trimmed `trial_id`:
  - Products index name: `harbor-products-${trial_id}`
  - Support index name: `harbor-support-${trial_id}`
  - Composite retriever name: `harbor-composite-${trial_id}`
- Use `SimpleDirectoryReader` from `llama_index.core` to load documents from each directory.
- Use `LlamaCloudIndex.from_documents(...)` from `llama_index.indices.managed.llama_cloud` to create each managed index with `project_name="Default"`.
- Build a `LlamaCloudCompositeRetriever` from `llama_index.indices.managed.llama_cloud` with:
  - `name="harbor-composite-${trial_id}"`
  - `project_name="Default"`
  - `create_if_not_exists=True`
  - `mode=CompositeRetrievalMode.FULL` (import `CompositeRetrievalMode` from `llama_cloud`)
  - `rerank_top_n=5`
- Attach **both** managed indexes to the composite retriever via `composite_retriever.add_index(<index>, description=<description>)`. Use these descriptions verbatim:
  - Products index description: `Product specifications and technical details for Acme Widgets Corporation products.`
  - Support index description: `Customer support FAQ and troubleshooting guides for Acme Widgets Corporation.`
- Run the user-supplied query against the composite retriever via `composite_retriever.retrieve(<query>)`.
- Write the retrieved nodes to the `--output` file (UTF-8). Each retrieved node must be written as a single line in the format `score=<score>: <text>` followed by a newline, in the order returned by `.retrieve(...)`. `<score>` should be `node.score` formatted via `repr(...)` (so `None` scores render as `None`); `<text>` should be `node.get_content()` with all newline characters replaced by a single space.
- Print exactly one line to stdout: `Retriever name: harbor-composite-${trial_id}` where `${trial_id}` is replaced by the trimmed value from `/logs/artifacts/trial_id`.
- The script must exit with status code `0` on success and a non-zero status code when either `--products-dir` or `--support-dir` does not exist (or is not a directory).

## Implementation Guide
1. Parse `--products-dir`, `--support-dir`, `--query`, and `--output` using `argparse` (standard library).
2. Open `/logs/artifacts/trial_id`, read its content, and strip whitespace to obtain `trial_id`.
3. Validate that both `--products-dir` and `--support-dir` exist and are directories; if not, exit with a non-zero status code.
4. Load documents for each folder via `SimpleDirectoryReader(<dir>).load_data()`.
5. Create each managed index, e.g.:
   ```python
   from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
   products_index = LlamaCloudIndex.from_documents(
       products_documents,
       name=f"harbor-products-{trial_id}",
       project_name="Default",
   )
   ```
6. Build the composite retriever and attach both indexes:
   ```python
   from llama_cloud import CompositeRetrievalMode
   from llama_index.indices.managed.llama_cloud import LlamaCloudCompositeRetriever
   composite_retriever = LlamaCloudCompositeRetriever(
       name=f"harbor-composite-{trial_id}",
       project_name="Default",
       create_if_not_exists=True,
       mode=CompositeRetrievalMode.FULL,
       rerank_top_n=5,
   )
   composite_retriever.add_index(products_index, description="...")
   composite_retriever.add_index(support_index, description="...")
   ```
7. Call `nodes = composite_retriever.retrieve(<query>)` and write `score=<repr(node.score)>: <flattened-text>` lines (one node per line) to `--output`.
8. Print the `Retriever name: harbor-composite-<trial_id>` line.
9. Return exit code 0.

## Acceptance Criteria
- Project path: /home/user/myproject
- Script path: /home/user/myproject/composite.py
- Command: `python3 composite.py --products-dir <products_dir> --support-dir <support_dir> --query <query> --output <output_path>`
- Input argument format: `--products-dir <path>`, `--support-dir <path>`, `--query <query_string>`, `--output <path_to_text_file>`.
- Expected command stdout: includes exactly one line `Retriever name: harbor-composite-<trial_id>` where `<trial_id>` is read (and stripped) from `/logs/artifacts/trial_id`.
- Two new LlamaCloud pipelines named `harbor-products-<trial_id>` and `harbor-support-<trial_id>` must exist in the `Default` project after the script runs.
- A new LlamaCloud retriever named `harbor-composite-<trial_id>` must exist (queryable via the `GET /api/v1/retrievers` REST endpoint). The retriever must have **exactly two** attached pipelines, whose IDs match the two indexes above.
- The `--output` file must be created, must be non-empty, and each line must start with `score=` (one line per retrieved node).
- The script must call `LlamaCloudIndex.from_documents` from `llama_index.indices.managed.llama_cloud` for each managed index with `project_name="Default"`.
- The script must use `LlamaCloudCompositeRetriever` with `mode=CompositeRetrievalMode.FULL` and `rerank_top_n=5`, and must call `add_index` twice.
- The script must exit with a non-zero status code when either `--products-dir` or `--support-dir` does not exist.

