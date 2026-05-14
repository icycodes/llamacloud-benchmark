# LlamaCloud Parse v2 Request Payload Builder

## Background
LlamaCloud's Parse v2 API requires every parse request to include both a `tier` and a `version`. The four valid tiers are `fast`, `cost_effective`, `agentic`, and `agentic_plus`. The `version` value must be either `latest` (for development) or a pinned dated release in `YYYY-MM-DD` format (for production). Each request can also request specific output sections through an `expand` list whose allowed values are `text`, `markdown`, `items`, and `images_content_metadata`. A well-known gotcha is that the `fast` tier does NOT support markdown output: requesting `markdown` in `expand` for a `fast`-tier job returns a validation error from the LlamaCloud API, so teams catch this client-side before submitting batches.

Production teams typically describe their batch of parse jobs in a YAML manifest, validate the manifest offline, and emit a JSON list of ready-to-submit Parse v2 request payloads. You must build that offline, fully self-contained CLI utility.

The utility must demonstrate that the LlamaCloud SDK is installed and importable by importing `LlamaCloud` from the `llama_cloud` package at module top level. However, it MUST NOT instantiate the client and MUST NOT make any outbound HTTP request.

## Requirements
- Implement a Python CLI script `build_requests.py` that imports, at module top level (verbatim): `from llama_cloud import LlamaCloud`. The script MUST NOT instantiate `LlamaCloud`, and MUST NOT make any network request.
- The CLI must accept the following arguments:
  - `--config` (required): absolute path to a YAML manifest file (schema described below).
  - `--output` (required): absolute path of the JSON request bundle to write.
- The YAML config has this exact schema:
  ```yaml
  requests:
    - file_id: <non-empty string>
      tier: fast | cost_effective | agentic | agentic_plus
      version: latest | YYYY-MM-DD
      expand: [<allowed value>, ...]   # optional; default is the empty list
  ```
  - `requests` is a non-empty list.
  - `tier` must be one of exactly four lowercase strings: `fast`, `cost_effective`, `agentic`, `agentic_plus`.
  - `version` must be either the literal string `latest` OR a date string that matches the regex `^\d{4}-\d{2}-\d{2}$` (any 4-digit year, 2-digit month, 2-digit day separated by single dashes). No further calendar validation is required.
  - `expand`, when present, must be a list of strings. Allowed values are: `text`, `markdown`, `items`, `images_content_metadata`.
  - If `expand` is omitted, treat it as an empty list `[]` in the output.
- The script must validate the config and on the FIRST failure print exactly one error line to stderr in the format `Error: <message>` and exit with a non-zero status code (and NOT write any output file). The exact error messages required are:
  - `Error: config file not found: <config_path>` - when `--config` does not exist on disk.
  - `Error: requests must be a non-empty list`
  - `Error: requests[<i>].file_id must be a non-empty string`
  - `Error: requests[<i>].tier must be one of: agentic, agentic_plus, cost_effective, fast`
  - `Error: requests[<i>].version must be 'latest' or a date string in YYYY-MM-DD format`
  - `Error: requests[<i>].expand must be a list of strings`
  - `Error: requests[<i>].expand contains unsupported value '<value>'. Allowed: text, markdown, items, images_content_metadata`
  - `Error: requests[<i>] uses tier 'fast' which does not support 'markdown' in expand`
  The check order is: file existence -> `requests` is non-empty list -> per-entry checks in list order, and within each entry: `file_id` -> `tier` -> `version` -> `expand` is list of strings -> per-element allowed-value check -> fast/markdown incompatibility check.
- On success, the script must write a JSON file at `--output` with this exact top-level shape (no extra keys):
  ```json
  {
    "requests": [
      {
        "file_id": "<string>",
        "tier": "<one of the four tiers>",
        "version": "<latest or YYYY-MM-DD>",
        "expand": ["<allowed value>", ...]
      }
    ],
    "summary": {
      "total": <int>,
      "by_tier": {
        "fast": <int>,
        "cost_effective": <int>,
        "agentic": <int>,
        "agentic_plus": <int>
      }
    }
  }
  ```
  - The order of entries in `requests` MUST preserve the order from the YAML manifest (do NOT sort).
  - Each entry MUST include all four fields `file_id`, `tier`, `version`, `expand` (with `expand` defaulting to `[]` when omitted in the YAML).
  - `summary.total` MUST equal `len(requests)`.
  - `summary.by_tier` MUST include all four keys, each set to the integer count of requests using that tier (0 if unused).
  - Write the JSON with `json.dump(..., indent=2)` so the file is human-readable.
- On success, the script must print exactly one line to stdout and exit `0`:
  `Built <N> Parse v2 requests at <output_path>: fast=<F> cost_effective=<C> agentic=<A> agentic_plus=<P>`
  where `<N>` is the integer count of requests and `<F>/<C>/<A>/<P>` are the per-tier counts in that exact order.

## Implementation Guide
1. The project directory `/home/user/parse_requests` already exists and contains a starter YAML config at `/home/user/parse_requests/configs/valid.yaml` describing four requests (one per tier). Do NOT modify or delete that file.
2. Create the script at `/home/user/parse_requests/build_requests.py`.
3. Use `argparse` for argument parsing and `pyyaml` (`import yaml`) for parsing the manifest. Both packages are pre-installed.
4. Import the SDK class at module top level exactly as listed in the Requirements (this is verified by string match against the script source).
5. Run the validation checks in the listed order. For each failure, print `Error: <message>` to `sys.stderr` and `sys.exit(1)`. Do NOT print to stdout in the error path. Do NOT create the output file in the error path.
6. Build the output JSON with the requested shape, write it with `json.dump(..., indent=2)`, print the success line, exit `0`.
7. Use `re.fullmatch(r"\d{4}-\d{2}-\d{2}", value)` (or equivalent) for the date format check. The literal string `latest` is accepted as-is.

## Acceptance Criteria
- Project path: /home/user/parse_requests
- Script path: /home/user/parse_requests/build_requests.py
- Command (happy path): `python3 /home/user/parse_requests/build_requests.py --config /home/user/parse_requests/configs/valid.yaml --output /home/user/parse_requests/plan.json`
  - Exit code: `0`.
  - Stdout (exact single line): `Built 4 Parse v2 requests at /home/user/parse_requests/plan.json: fast=1 cost_effective=1 agentic=1 agentic_plus=1`
  - The file `/home/user/parse_requests/plan.json` exists and is valid JSON with the schema described above.
  - `requests` has length 4. In the original YAML order, the entries are:
    - Index 0: `{"file_id": "file_aaa", "tier": "agentic", "version": "latest", "expand": ["text", "markdown"]}`
    - Index 1: `{"file_id": "file_bbb", "tier": "agentic_plus", "version": "2026-01-08", "expand": ["markdown", "items"]}`
    - Index 2: `{"file_id": "file_ccc", "tier": "fast", "version": "latest", "expand": ["text"]}`
    - Index 3: `{"file_id": "file_ddd", "tier": "cost_effective", "version": "latest", "expand": []}`
  - `summary` equals `{"total": 4, "by_tier": {"fast": 1, "cost_effective": 1, "agentic": 1, "agentic_plus": 1}}`.
- Command (validation error - bad tier): the user must create a config file at `/home/user/parse_requests/configs/bad_tier.yaml` with the following exact contents:
  ```yaml
  requests:
    - file_id: file_xxx
      tier: premium
      version: latest
      expand: [markdown]
  ```
  Then run: `python3 /home/user/parse_requests/build_requests.py --config /home/user/parse_requests/configs/bad_tier.yaml --output /home/user/parse_requests/bad_tier_plan.json`
  - Exit code: non-zero.
  - Stderr (exact line): `Error: requests[0].tier must be one of: agentic, agentic_plus, cost_effective, fast`
  - The file `/home/user/parse_requests/bad_tier_plan.json` MUST NOT be created.
- Command (validation error - fast tier with markdown): the user must create a config file at `/home/user/parse_requests/configs/fast_markdown.yaml` with the following exact contents:
  ```yaml
  requests:
    - file_id: file_yyy
      tier: fast
      version: latest
      expand: [text, markdown]
  ```
  Then run: `python3 /home/user/parse_requests/build_requests.py --config /home/user/parse_requests/configs/fast_markdown.yaml --output /home/user/parse_requests/fast_markdown_plan.json`
  - Exit code: non-zero.
  - Stderr (exact line): `Error: requests[0] uses tier 'fast' which does not support 'markdown' in expand`
  - The file `/home/user/parse_requests/fast_markdown_plan.json` MUST NOT be created.
- Command (validation error - bad version): the user must create a config file at `/home/user/parse_requests/configs/bad_version.yaml` with the following exact contents:
  ```yaml
  requests:
    - file_id: file_zzz
      tier: agentic
      version: jan-8-2026
      expand: [markdown]
  ```
  Then run: `python3 /home/user/parse_requests/build_requests.py --config /home/user/parse_requests/configs/bad_version.yaml --output /home/user/parse_requests/bad_version_plan.json`
  - Exit code: non-zero.
  - Stderr (exact line): `Error: requests[0].version must be 'latest' or a date string in YYYY-MM-DD format`
  - The file `/home/user/parse_requests/bad_version_plan.json` MUST NOT be created.
- Command (validation error - missing config file): `python3 /home/user/parse_requests/build_requests.py --config /home/user/parse_requests/configs/no_such_file.yaml --output /home/user/parse_requests/should_not_exist.json`
  - Exit code: non-zero.
  - Stderr (exact line): `Error: config file not found: /home/user/parse_requests/configs/no_such_file.yaml`
  - The file `/home/user/parse_requests/should_not_exist.json` MUST NOT be created.
- SDK usage: the script source must contain the verbatim substring `from llama_cloud import LlamaCloud`.

