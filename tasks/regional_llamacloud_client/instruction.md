# Region-Aware LlamaCloud Client Configurator

## Background
LlamaCloud is offered in two distinct regions: North America (NA) and the European Union (EU). Each region has its own API endpoint, and users must explicitly point the SDK client to the EU endpoint via the `base_url` parameter to avoid silent 401/403 authentication errors. This is a well-known friction point for teams operating across regions.

You must build a small Python CLI utility that constructs a `LlamaCloud` client (from the `llama-cloud` Python SDK) using the correct regional endpoint and writes a structured report describing the resolved configuration.

## Requirements
- Implement a Python CLI script `region_setup.py` that uses the `llama_cloud.client.LlamaCloud` SDK class.
- The CLI must accept two arguments:
  - `--region` (required): one of `na` or `eu` (case-insensitive).
  - `--output` (required): the path to a JSON file where the configuration report will be written.
- The script must map the region string to the correct LlamaCloud API endpoint:
  - `na` -> `https://api.cloud.llamaindex.ai`
  - `eu` -> `https://api.cloud.eu.llamaindex.ai`
- The script must instantiate a `LlamaCloud` client using the `LLAMA_CLOUD_API_KEY` environment variable as the token and the resolved `base_url`.
- After instantiation, the script must write a JSON object to the `--output` path with the following exact shape:
  ```json
  {
    "region": "NA" | "EU",
    "base_url": "https://api.cloud.llamaindex.ai" | "https://api.cloud.eu.llamaindex.ai",
    "client_initialized": true
  }
  ```
  The `region` field MUST be the uppercase code (`NA` or `EU`).
- The script must print a single line to stdout in this exact format (using the resolved values):
  `Configured LlamaCloud client for region=<NA|EU> base_url=<resolved_url>`
- If `--region` is anything other than `na`/`eu` (case-insensitive), the script MUST exit with a non-zero status code and print an error message to stderr in this exact format: `Error: unsupported region '<value>'. Use 'na' or 'eu'.`
- The script MUST NOT make any outbound HTTP calls. The verification environment does not validate against the real LlamaCloud servers.

## Implementation Guide
1. Create the project directory `/home/user/llamacloud_region`.
2. Inside it, create `region_setup.py`. Use Python's `argparse` for argument parsing.
3. Import the SDK:
   ```python
   from llama_cloud.client import LlamaCloud
   ```
4. Map the lowercase region to the proper base URL and uppercase code.
5. Instantiate the client:
   ```python
   client = LlamaCloud(token=os.environ.get("LLAMA_CLOUD_API_KEY", ""), base_url=base_url)
   ```
6. Write the JSON report to the `--output` path.
7. Print the required confirmation line to stdout and exit with status `0`.
8. For an invalid region argument, write the error to stderr and exit with status `1`.

## Acceptance Criteria
- Project path: /home/user/llamacloud_region
- Script path: /home/user/llamacloud_region/region_setup.py
- Command (NA): `python3 /home/user/llamacloud_region/region_setup.py --region na --output /home/user/llamacloud_region/na_report.json`
  - Exit code: `0`
  - Stdout must contain exactly: `Configured LlamaCloud client for region=NA base_url=https://api.cloud.llamaindex.ai`
  - The file `/home/user/llamacloud_region/na_report.json` must exist and contain JSON with `region` set to `"NA"`, `base_url` set to `"https://api.cloud.llamaindex.ai"`, and `client_initialized` set to `true`.
- Command (EU): `python3 /home/user/llamacloud_region/region_setup.py --region EU --output /home/user/llamacloud_region/eu_report.json`
  - Exit code: `0`
  - Stdout must contain exactly: `Configured LlamaCloud client for region=EU base_url=https://api.cloud.eu.llamaindex.ai`
  - The file `/home/user/llamacloud_region/eu_report.json` must exist and contain JSON with `region` set to `"EU"`, `base_url` set to `"https://api.cloud.eu.llamaindex.ai"`, and `client_initialized` set to `true`.
- Command (invalid): `python3 /home/user/llamacloud_region/region_setup.py --region apac --output /tmp/should_not_exist.json`
  - Exit code: non-zero (e.g., `1`).
  - Stderr must contain: `Error: unsupported region 'apac'. Use 'na' or 'eu'.`
  - The output file `/tmp/should_not_exist.json` must NOT be created.

