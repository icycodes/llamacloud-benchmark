# Configure a Region-Aware LlamaCloud Client (Python)

## Background
LlamaCloud offers two managed deployments: a default **North America (NA)** region and a separate **Europe (EU)** region. Each region has its own base URL, and a client created against the wrong base URL silently produces authentication errors instead of working requests. Your job is to build a small Python command-line utility that uses the [LlamaCloud Python SDK](https://developers.llamaindex.ai/reference/python/) (the `llama-cloud` package) to construct a region-aware `LlamaCloud` client and persist its resolved configuration to disk.

The SDK is already installed in the environment and the `LLAMA_CLOUD_API_KEY` environment variable is configured for the **NA** region (the default region). You do NOT need to handle authentication explicitly — the SDK reads the API key from the environment automatically.

The two valid regional base URLs are:
- **NA (`us`)**: `https://api.cloud.llamaindex.ai`
- **EU (`eu`)**: `https://api.cloud.eu.llamaindex.ai`

## Requirements
- Implement a Python CLI named `region_client.py` at `/home/user/myproject/region_client.py`.
- The script must accept exactly these command-line arguments:
  - `--region <us|eu>` (**required**): the LlamaCloud region. Comparison must be case-insensitive (i.e. `US`, `Us`, `eu`, `EU` are all valid). Any other value (for example `apac` or an empty string) MUST cause the script to exit with a non-zero status code.
  - `--output <path>` (**required**): the path where the resolved client configuration must be written as JSON.
  - `--check` (**optional flag**): when present, the script must perform a real connectivity check against the configured base URL by calling the SDK to list projects (see Implementation Guide).
- The script must use the **`llama-cloud`** Python SDK (`from llama_cloud import LlamaCloud`).
- Map the (case-insensitive) region argument to a base URL using exactly these two literals:
  - `us` → `https://api.cloud.llamaindex.ai`
  - `eu` → `https://api.cloud.eu.llamaindex.ai`
- Instantiate the client using the keyword argument `base_url=<resolved_url>` (i.e. the resolved URL must be passed to the `LlamaCloud(...)` constructor via the `base_url` keyword).
- After constructing the client, write a single JSON object to the `--output` path (UTF-8, with `indent=2`) containing **exactly** these fields, with **exactly** these names:
  - `region`: the lowercased region string (`"us"` or `"eu"`).
  - `base_url`: the resolved base URL string for the region (one of the two literals above).
  - `connection_verified`: a JSON boolean. Must be `true` only when `--check` was supplied AND the project-listing call returned successfully without raising an exception. Must be `false` in every other case.
  - `project_count`: a JSON integer. Must be the number of projects returned by the project-listing call when `--check` succeeded. Must be `0` when `--check` was not supplied or when the project-listing call failed.
- After a successful run, print exactly one line to stdout in the **exact** format: `Region: <region> | Base URL: <base_url>` (single space around the pipe), where `<region>` is the lowercased region string and `<base_url>` is the resolved URL.
- The script must exit with status code `0` on success (including when `--check` is omitted) and with a non-zero status code on argument-validation errors (such as an unknown region).

## Implementation Guide
1. Parse `--region`, `--output`, and the flag `--check` using `argparse` (standard library).
2. Normalize `--region` to lowercase, then look it up in a dict that maps `"us"` and `"eu"` to their respective base URLs. If the value is unknown, exit with a non-zero status code (you may print an error to stderr).
3. Construct the client:
   ```python
   from llama_cloud import LlamaCloud
   client = LlamaCloud(base_url=resolved_url)
   ```
4. If `--check` is supplied, list the projects via the SDK using `client.projects.list()`. Convert the iterable to a `list(...)` so you can take its length. Wrap the call in a `try/except` so any SDK exception (network error, auth failure, etc.) results in `connection_verified=false` and `project_count=0` rather than a crash.
5. Build the summary dictionary with the four required fields and write it to `--output` using `json.dump(summary, fp, indent=2)`.
6. Print the line `Region: <region> | Base URL: <base_url>` to stdout.
7. Return exit code 0.

## Acceptance Criteria
- Project path: /home/user/myproject
- Script path: /home/user/myproject/region_client.py
- Command: `python3 region_client.py --region <us|eu> --output <path_to_json> [--check]`
- Input argument format: `--region <us|eu>` (case-insensitive), `--output <path_to_json_file>`, optional `--check` flag.
- Expected stdout: includes exactly one line `Region: <region> | Base URL: <base_url>` where `<region>` is the lowercased input region (`us` or `eu`) and `<base_url>` is the matching literal URL.
- The `--output` JSON file must be created at the path specified by `--output` and must contain exactly the four fields `region`, `base_url`, `connection_verified`, and `project_count` with the semantics described in Requirements.
- When `--region us --check` is supplied, the JSON file must contain `connection_verified: true` and `project_count` must be an integer `>= 1` (the configured account has at least one project).
- When `--region eu` is supplied without `--check`, the JSON file must contain `base_url: "https://api.cloud.eu.llamaindex.ai"`, `connection_verified: false`, and `project_count: 0` (no API call is made).
- The script must use `LlamaCloud(base_url=...)` from the `llama_cloud` package to construct the client.
- The script must exit with a non-zero status code when given an unknown region value (for example `--region apac`).

