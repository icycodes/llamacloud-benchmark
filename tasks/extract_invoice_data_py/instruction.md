# Extract Structured Invoice Data with LlamaExtract (Python)

## Background
LlamaCloud's LlamaExtract service turns unstructured documents into clean, schema-validated JSON. You are given a deterministic invoice PDF at `/home/user/extract_task/invoice.pdf` that was generated when the environment was built. Build a small Python script that uploads the invoice to LlamaCloud, runs LlamaExtract against a Pydantic-defined schema, and writes the resulting structured object to a JSON file so a downstream verifier can audit the fields.

## Requirements
- Read the current `trial_id` from `/logs/artifacts/trial_id`.
- Build a Python script `extract.py` in `/home/user/extract_task` that:
  - Authenticates against LlamaCloud using the `LLAMA_CLOUD_API_KEY` environment variable (read by the SDK from the environment).
  - Uploads `/home/user/extract_task/invoice.pdf` to the LlamaCloud `files` resource with `purpose="extract"`, using the literal external file id `harbor-invoice-${trial_id}.pdf` so concurrent runs do not collide on shared identifiers.
  - Defines a Pydantic schema named `Invoice` with the following fields (each with a `description` so LlamaExtract can locate them):
    - `invoice_number: str` — the invoice identifier printed on the document.
    - `vendor_name: str` — the name of the company issuing the invoice.
    - `customer_name: str` — the name of the company being billed.
    - `total_amount: float` — the grand total amount due in the invoice currency.
    - `currency: str` — the ISO 4217 currency code of the total amount.
  - Submits an extraction job with `client.extract.create(...)` using the JSON schema of the Pydantic `Invoice` model, `extraction_target="per_doc"`, and an `agentic` tier so the managed LLM is used.
  - Polls `client.extract.get(job.id)` until the job reaches a terminal status (`COMPLETED`, `FAILED`, or `CANCELLED`).
  - On success, writes the extracted object to `/home/user/extract_task/output.json` as UTF-8 JSON. The JSON file must be a single object that matches the `Invoice` schema (i.e. the top level is the object with `invoice_number`, `vendor_name`, `customer_name`, `total_amount`, `currency`).
  - Writes a companion log line `Extract job id: <job_id>` to `/home/user/extract_task/output.log` so the verifier can locate the job.
- The script must run end-to-end with `python3 extract.py` and exit with status `0`.

## Implementation Hints
- The LlamaCloud Python SDK is exposed via `from llama_cloud import LlamaCloud`. Instantiating `LlamaCloud()` automatically reads `LLAMA_CLOUD_API_KEY` from the environment.
- Upload the PDF with `client.files.create(file="/home/user/extract_task/invoice.pdf", purpose="extract", external_file_id=f"harbor-invoice-{trial_id}.pdf")`. The returned object exposes `.id`, which you pass as `file_input` to the extract job.
- Use `Invoice.model_json_schema()` (Pydantic v2) as the value for the `data_schema` configuration field.
- The extraction job is asynchronous: `client.extract.create(...)` returns immediately with a job id and a status. Poll with `client.extract.get(job.id)` every couple of seconds (e.g. `time.sleep(2)`) until `job.status` is one of `COMPLETED`, `FAILED`, or `CANCELLED`.
- On `COMPLETED`, the extracted payload is on `job.extract_result` (a dict that already matches your schema). Serialize it with `json.dumps(...)`.
- Make sure the JSON written to `output.json` has the schema fields at the top level. If the SDK returns the result wrapped in metadata, unwrap to the actual `Invoice` payload before writing.

## Acceptance Criteria
- Project path: `/home/user/extract_task`
- Script path: `/home/user/extract_task/extract.py`
- Output file: `/home/user/extract_task/output.json`
- Log file: `/home/user/extract_task/output.log`
- Command: `python3 /home/user/extract_task/extract.py`
  - The command must exit with status code `0`.
- LlamaCloud usage:
  - The script must use `from llama_cloud import LlamaCloud` (the official LlamaCloud Python SDK shipped via the `llama-cloud` package).
  - The uploaded file must use the LlamaCloud `external_file_id` value `harbor-invoice-${trial_id}.pdf` where `trial_id` is read from `/logs/artifacts/trial_id`.
- `output.json` must be valid UTF-8 JSON and decode into a single JSON object whose top level keys are exactly `invoice_number`, `vendor_name`, `customer_name`, `total_amount`, `currency` (no extra wrapping under `data`, `result`, etc.).
- `output.log` must contain a line matching the pattern `Extract job id: <job_id>` where `<job_id>` is the id of the extract job returned by LlamaCloud.

