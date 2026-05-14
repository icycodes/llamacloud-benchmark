# LlamaCloud Composite Retriever Plan Builder

## Background
When a team manages multiple LlamaCloud indices (for example, a `slides_index` for meeting decks and a `financial_index` for SEC filings), they typically expose them to an LLM agent via `LlamaCloudCompositeRetriever`. The composite retriever supports two modes: `CompositeRetrievalMode.FULL` (query every sub-index and globally rerank) and `CompositeRetrievalMode.ROUTING` (let an agent pick the best sub-index based on its `description`). In `ROUTING` mode the per-index `description` is critical because that is the only signal the router has, so every sub-index MUST have a non-empty description. Composite retrievers also accept a `rerank_top_n` knob (positive integer) that bounds how many nodes survive reranking.

Production teams almost always commit a YAML config describing the composite retriever and validate it offline before applying it with the SDK. You must build a small, fully offline Python CLI that:

1. Imports `LlamaCloudCompositeRetriever` from `llama_index.indices.managed.llama_cloud` and `CompositeRetrievalMode` from `llama_cloud` at module top-level. These imports prove the SDK is wired up correctly, but they must NOT be called and no network requests may be made.
2. Reads a YAML config describing the composite retriever and the sub-indices to attach.
3. Validates the config against the rules below and emits an actionable JSON plan that downstream code (or an agent) can later feed into `LlamaCloudCompositeRetriever(...)` / `composite_retriever.add_index(...)` calls.

## Requirements
- Implement a Python CLI script `build_plan.py` that imports, at module top-level (verbatim):
  - `from llama_index.indices.managed.llama_cloud import LlamaCloudCompositeRetriever`
  - `from llama_cloud import CompositeRetrievalMode`
  The script MUST NOT instantiate `LlamaCloudCompositeRetriever` or `CompositeRetrievalMode`, and MUST NOT issue any HTTP request.
- The CLI must accept the following arguments:
  - `--config` (required): absolute path to a YAML config file (schema described below).
  - `--output` (required): absolute path of the JSON plan file to write.
- The YAML config has this exact schema:
  ```yaml
  retriever:
    name: <non-empty string>
    project_name: <non-empty string>
    mode: FULL | ROUTING       # case-insensitive in the config; output normalises to upper-case
    rerank_top_n: <positive integer>
    create_if_not_exists: <bool>
  sub_indices:
    - name: <non-empty string>
      project_name: <non-empty string>
      description: <non-empty string>
  ```
  - `sub_indices` is a list with at least 1 entry.
  - `mode` is matched case-insensitively. Any value other than `full`/`FULL` or `routing`/`ROUTING` is an error.
- The script must validate the config and on any validation failure print exactly one error line to stderr in the format `Error: <message>` and exit with a non-zero status code (and NOT write any output file). The exact error messages required are:
  - `Error: config file not found: <config_path>` - when `--config` does not exist on disk.
  - `Error: retriever.name must be a non-empty string`
  - `Error: retriever.project_name must be a non-empty string`
  - `Error: retriever.mode must be one of FULL or ROUTING (case-insensitive)`
  - `Error: retriever.rerank_top_n must be a positive integer`
  - `Error: sub_indices must be a non-empty list`
  - `Error: sub_indices[<i>].name must be a non-empty string`
  - `Error: sub_indices[<i>].project_name must be a non-empty string`
  - `Error: sub_indices[<i>].description must be a non-empty string` (this rule applies in BOTH modes; descriptions are always required)
  - `Error: sub_indices contains duplicate (name, project_name) pair: (<name>, <project_name>)`
  Validation MUST stop and report the FIRST failure encountered, in the listed order. The check order is: file existence -> retriever.name -> retriever.project_name -> retriever.mode -> retriever.rerank_top_n -> sub_indices is non-empty list -> per-entry checks in list order (name -> project_name -> description) -> duplicate pair check after all per-entry checks pass.
- On success, the script must write a JSON file at `--output` with this exact top-level shape (no extra keys):
  ```json
  {
    "retriever": {
      "name": "<retriever.name>",
      "project_name": "<retriever.project_name>",
      "mode": "FULL" | "ROUTING",
      "rerank_top_n": <int>,
      "create_if_not_exists": <bool>
    },
    "sub_indices": [
      {
        "name": "<name>",
        "project_name": "<project_name>",
        "description": "<description>"
      }
    ],
    "summary": {
      "sub_index_count": <int>,
      "mode": "FULL" | "ROUTING"
    }
  }
  ```
  - The `sub_indices` list in the output MUST preserve the original ordering from the YAML config (do NOT sort).
  - `summary.sub_index_count` MUST equal `len(sub_indices)`.
  - `mode` in the output MUST be upper-case (`FULL` or `ROUTING`) regardless of the case used in the config.
  - Write the JSON with `json.dump(..., indent=2)` so the file is human-readable.
- On success, the script must print exactly one line to stdout and exit `0`:
  `Composite retriever plan written to <output_path>: name=<retriever.name> mode=<MODE> sub_indices=<N>`
  where `<MODE>` is the normalised upper-case mode and `<N>` is the integer count of sub-indices.

## Implementation Guide
1. The project directory `/home/user/composite_planner` already exists and contains a starter `configs/valid.yaml` describing a two-index composite retriever (`slides_index` and `financial_index`). Do NOT modify or delete that file.
2. Create the script at `/home/user/composite_planner/build_plan.py`.
3. Use `argparse` for argument parsing and `pyyaml` (`import yaml`) for config parsing. Both packages are pre-installed.
4. Import the SDK classes at module top-level exactly as listed in the Requirements (these imports are verified by string match).
5. Run the validation checks in the listed order. For each failure, print `Error: <message>` to `sys.stderr` and `sys.exit(1)`. Do NOT print to stdout in the error path. Do NOT create the output file in the error path.
6. Normalise `mode` to upper-case (`FULL` or `ROUTING`) when writing the output and the stdout success line.
7. Write the JSON plan, print the success line, exit `0`.

## Acceptance Criteria
- Project path: /home/user/composite_planner
- Script path: /home/user/composite_planner/build_plan.py
- Command (happy path, FULL mode): `python3 /home/user/composite_planner/build_plan.py --config /home/user/composite_planner/configs/valid.yaml --output /home/user/composite_planner/plan.json`
  - Exit code: `0`.
  - Stdout (exact single line): `Composite retriever plan written to /home/user/composite_planner/plan.json: name=Essays Retriever mode=FULL sub_indices=2`
  - The file `/home/user/composite_planner/plan.json` exists and is valid JSON matching the schema above.
  - `retriever` equals `{"name": "Essays Retriever", "project_name": "Essays", "mode": "FULL", "rerank_top_n": 5, "create_if_not_exists": true}`.
  - `sub_indices` has length 2, with index 0 = `{"name": "slides_index", "project_name": "Essays", "description": "Information source for slide shows presented during team meetings"}` and index 1 = `{"name": "financial_index", "project_name": "Essays", "description": "Information source for company financial reports"}` (original order from the YAML preserved).
  - `summary` equals `{"sub_index_count": 2, "mode": "FULL"}`.
- Command (routing mode, lowercase in YAML): the user must create a new config at `/home/user/composite_planner/configs/routing.yaml` describing the SAME two sub-indices but with the following retriever block (verbatim values):
  ```yaml
  retriever:
    name: Routing Retriever
    project_name: Essays
    mode: routing
    rerank_top_n: 3
    create_if_not_exists: false
  sub_indices:
    - name: slides_index
      project_name: Essays
      description: Information source for slide shows presented during team meetings
    - name: financial_index
      project_name: Essays
      description: Information source for company financial reports
  ```
  Then run: `python3 /home/user/composite_planner/build_plan.py --config /home/user/composite_planner/configs/routing.yaml --output /home/user/composite_planner/routing_plan.json`
  - Exit code: `0`.
  - Stdout (exact single line): `Composite retriever plan written to /home/user/composite_planner/routing_plan.json: name=Routing Retriever mode=ROUTING sub_indices=2`
  - The output JSON `retriever.mode` is `"ROUTING"` (upper-cased) and `summary.mode` is `"ROUTING"`.
- Command (validation error - missing description in routing-style config): the user must create a config at `/home/user/composite_planner/configs/missing_desc.yaml` with a valid retriever block but with the SECOND sub-index missing the `description` field (set it to the empty string `""`):
  ```yaml
  retriever:
    name: Bad Retriever
    project_name: Essays
    mode: FULL
    rerank_top_n: 5
    create_if_not_exists: true
  sub_indices:
    - name: slides_index
      project_name: Essays
      description: Information source for slide shows presented during team meetings
    - name: financial_index
      project_name: Essays
      description: ""
  ```
  Then run: `python3 /home/user/composite_planner/build_plan.py --config /home/user/composite_planner/configs/missing_desc.yaml --output /home/user/composite_planner/bad_plan.json`
  - Exit code: non-zero.
  - Stderr (exact line): `Error: sub_indices[1].description must be a non-empty string`
  - The file `/home/user/composite_planner/bad_plan.json` MUST NOT be created.
- Command (validation error - missing config file): `python3 /home/user/composite_planner/build_plan.py --config /home/user/composite_planner/configs/no_such_file.yaml --output /home/user/composite_planner/should_not_exist.json`
  - Exit code: non-zero.
  - Stderr (exact line): `Error: config file not found: /home/user/composite_planner/configs/no_such_file.yaml`
  - The file `/home/user/composite_planner/should_not_exist.json` MUST NOT be created.
- SDK usage: the script source must contain BOTH of the following verbatim substrings:
  - `from llama_index.indices.managed.llama_cloud import LlamaCloudCompositeRetriever`
  - `from llama_cloud import CompositeRetrievalMode`

