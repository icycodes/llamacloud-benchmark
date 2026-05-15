# Cross-Index Retrieval with `LlamaCloudCompositeRetriever`

## Background
You are building a small Retrieval-Augmented Generation (RAG) prototype on **LlamaCloud** that needs to answer questions whose evidence is spread across **two separate managed indices**. LlamaCloud exposes a dedicated `LlamaCloudCompositeRetriever` class that lets you query several `LlamaCloudIndex` instances together and rerank the unioned nodes server-side, without needing a separate LLM API key (we use `CompositeRetrievalMode.FULL`).

The Python SDKs `llama-index-core` and `llama-cloud-services` are already installed in the environment. The LlamaCloud account is already provisioned and the API key is exposed via the environment variable `LLAMA_CLOUD_API_KEY`. The default project name to use is `Default`.

Two pre-staged, plain-text corpora exist on disk:

- `/home/user/myproject/docs_astronomy/` contains a file describing a fictional internal initiative named **Project Aurora**, whose stated mission is to *catalog every star in the Milky Way*.
- `/home/user/myproject/docs_cooking/` contains a short **Honey Lemon Tea** recipe that boils 250 ml of water with honey and lemon juice.

Because this task may run multiple times concurrently against the same LlamaCloud project, every externally visible name **MUST be unique per trial run**: read the `trial_id` from `/logs/artifacts/trial_id` and append it as a suffix to every base name listed below.

## Requirements
Write a Python script at `/home/user/myproject/build_composite.py` that:
- Reads the `trial_id` value from `/logs/artifacts/trial_id`.
- Builds two **separate** managed `LlamaCloudIndex` instances against project `Default`, using documents loaded from the two pre-staged folders:
  - From `/home/user/myproject/docs_astronomy/` create an index named `harbor-cmp-astro-<trial_id>`.
  - From `/home/user/myproject/docs_cooking/` create an index named `harbor-cmp-cook-<trial_id>`.
- Creates a `LlamaCloudCompositeRetriever` in the same project with:
  - `name = "harbor-cmp-retriever-<trial_id>"`,
  - `create_if_not_exists = True`,
  - `mode = CompositeRetrievalMode.FULL`,
  - `rerank_top_n = 5`.
- Attaches **both** indices to the composite retriever via `add_index(...)`. Provide a short, distinguishing `description` for each (for example, `"Astronomy notes about Project Aurora"` and `"Cooking recipes including Honey Lemon Tea"`).
- Uses the composite retriever to retrieve nodes for **two** queries (in this exact order):
  1. `astronomy_query`: `What is the mission of Project Aurora?`
  2. `cooking_query`: `How do you make Honey Lemon Tea?`
- Writes a Markdown summary to `/home/user/myproject/output.md` containing the headings below (in this order) and the **full text of the top-1 retrieved node** under each sub-heading:
  - `# LlamaCloud Composite Retrieval Result`
  - `## Astronomy Query Top Node`
  - `## Cooking Query Top Node`
- Writes a plain-text log to `/home/user/myproject/output.log` containing at minimum the following five lines (one fact per line), using the actual `trial_id` value:
  - `trial_id: <trial_id>`
  - `astro_index_name: harbor-cmp-astro-<trial_id>`
  - `cook_index_name: harbor-cmp-cook-<trial_id>`
  - `composite_retriever_name: harbor-cmp-retriever-<trial_id>`
  - `astro_num_retrieved: <Na>` and `cook_num_retrieved: <Nc>` where each is a positive integer giving the number of nodes returned for that query.

## Implementation Hints
- Import `LlamaCloudIndex` and `LlamaCloudCompositeRetriever` from `llama_cloud_services` (they are re-exported there), and `CompositeRetrievalMode` from `llama_cloud`.
- Use `from llama_index.core import SimpleDirectoryReader` to load each folder into a list of `Document` objects.
- `LlamaCloudIndex.from_documents(documents, name=..., project_name="Default", api_key=...)` blocks until ingestion is finished and returns a ready-to-use index.
- The composite retriever's `.retrieve(query)` method returns a list of `NodeWithScore` objects; each has `.node.get_content()` (or `.node.text`) and `.score` attributes. Use the node with the highest score as the "top-1" node.
- The script must run end to end with `python3 build_composite.py` from `/home/user/myproject` and exit with status code `0`.

## Acceptance Criteria
- Project path: `/home/user/myproject`
- Script path: `/home/user/myproject/build_composite.py`
- Command: `python3 build_composite.py` (run from `/home/user/myproject`)
- The script must exit with return code `0`.
- Two managed LlamaCloud indices must exist in project `Default` after the script runs, with names exactly equal to `harbor-cmp-astro-<trial_id>` and `harbor-cmp-cook-<trial_id>`, where `<trial_id>` is the value of `/logs/artifacts/trial_id`.
- Output files created by the script:
  - `/home/user/myproject/output.md` — non-empty Markdown that contains, in order:
    - The heading `# LlamaCloud Composite Retrieval Result`.
    - The sub-heading `## Astronomy Query Top Node` followed by text that mentions both `Project Aurora` and the phrase `catalog every star in the Milky Way` (case-insensitive).
    - The sub-heading `## Cooking Query Top Node` followed by text that mentions both `honey` and `lemon` (case-insensitive).
  - `/home/user/myproject/output.log` — must contain lines matching:
    - `trial_id: <trial_id>` where `<trial_id>` equals the value in `/logs/artifacts/trial_id`.
    - `astro_index_name: harbor-cmp-astro-<trial_id>`
    - `cook_index_name: harbor-cmp-cook-<trial_id>`
    - `composite_retriever_name: harbor-cmp-retriever-<trial_id>`
    - `astro_num_retrieved: <Na>` where `<Na>` is a positive integer (>= 1).
    - `cook_num_retrieved: <Nc>` where `<Nc>` is a positive integer (>= 1).

