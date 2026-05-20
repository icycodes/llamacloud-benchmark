# LlamaCloud Regional Client Setup (Python)

## Background
LlamaCloud is hosted in multiple regions: North America (the default) and the European Union. API keys are region-specific, so users must point the SDK at the correct regional endpoint or all requests will fail with `401 Unauthorized` errors. Build a small Python CLI that constructs a `LlamaParse` client targeted at the requested region and reports the resolved configuration so it can be wired into a larger pipeline.

## Requirements
- Implement a Python CLI script that selects the correct LlamaCloud base URL for the requested region and constructs a real `LlamaParse` client from the `llama-cloud-services` package.
- The CLI must accept a `--region` argument with values `us` or `eu` (case-insensitive).
- The CLI must read the API key from the `LLAMA_CLOUD_API_KEY` environment variable. Use a placeholder value such as `"llx-dummy"` if the variable is empty so the SDK can still be instantiated.
- The CLI must print exactly one line of JSON to standard output containing the resolved configuration (see `Acceptance Criteria` for the schema).
- For unsupported regions, the CLI must exit with a non-zero status code and emit an error message on standard error.

## Implementation Hints
- Install the official `llama-cloud-services` Python package and import `LlamaParse` and the `EU_BASE_URL` constant from it.
- The default (NA / US) base URL is `https://api.cloud.llamaindex.ai`; the EU base URL is exported by the SDK as the `EU_BASE_URL` constant (`https://api.cloud.eu.llamaindex.ai`).
- When building the JSON output, read the `base_url` back from the constructed `LlamaParse` instance to confirm that the SDK accepted the configuration.
- Use `argparse` (or any equivalent) to parse the CLI argument, and `json.dumps` to emit the result.

## Acceptance Criteria
- Project path: /home/user/myproject
- Command: `python3 /home/user/myproject/regional_client.py --region <region>`
- Command input argument format: `--region <us|eu>` (case-insensitive).
- For a recognized region, the command exits with status code `0` and prints a single JSON object on standard output with this shape:

  ```json
  {
    "region": "us" | "eu",
    "base_url": "https://api.cloud.llamaindex.ai" | "https://api.cloud.eu.llamaindex.ai",
    "parser_base_url": "https://api.cloud.llamaindex.ai" | "https://api.cloud.eu.llamaindex.ai"
  }
  ```

  - `region`: lowercase, matching the requested region.
  - `base_url`: the canonical regional endpoint chosen by the CLI.
  - `parser_base_url`: the `base_url` read back from the constructed `LlamaParse` instance.
- For any other region value (e.g. `apac`, empty string, missing argument), the command exits with a non-zero status code and prints an error message containing the substring `unsupported region` on standard error.

