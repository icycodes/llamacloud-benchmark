# Parse a PDF to Markdown with LlamaParse

## Background
You are tasked with using **LlamaParse** (a managed parsing service from LlamaCloud, accessed through the `llama-cloud-services` Python SDK) to convert a PDF document into clean Markdown that downstream RAG pipelines can index. LlamaParse is exposed via the `LlamaParse` class and produces markdown output that preserves headings and tables much better than naive PDF text extraction.

The LlamaCloud account has already been provisioned and the API key is available in the environment variable `LLAMA_CLOUD_API_KEY`. A sample PDF named `sample.pdf` is already present in the project directory. It is a short business-style report whose first heading reads `Quarterly Sales Report` and which contains a small table of products and revenues.

## Requirements
- Write a Python script `parse_doc.py` in `/home/user/myproject` that:
  - Reads the `trial_id` value from the file `/logs/artifacts/trial_id`.
  - Uses `LlamaParse` from `llama_cloud_services` (synchronous mode, markdown result) to parse `/home/user/myproject/sample.pdf`.
  - Writes the combined markdown text to `/home/user/myproject/output.md`.
  - Writes a plain-text log to `/home/user/myproject/output.log` containing at minimum these two lines:
    - `trial_id: <trial_id>` — where `<trial_id>` is the value read from `/logs/artifacts/trial_id`.
    - `pages_parsed: <N>` — where `<N>` is the number of pages (or document objects) returned by LlamaParse.

## Implementation Hints
- Install or rely on the pre-installed `llama-cloud-services` package and import `LlamaParse` from `llama_cloud_services`.
- Instantiate the parser with `result_type="markdown"` so that each returned document carries markdown text.
- The classic `load_data(file_path)` entry point returns a list of `Document`-like objects; concatenate their `text` (or `get_content()`) fields with blank lines between them to produce a single markdown file.
- Make sure your script reads `LLAMA_CLOUD_API_KEY` from the environment (the SDK picks it up automatically).
- The script must be executable with `python3 parse_doc.py` from `/home/user/myproject`.

## Acceptance Criteria
- Project path: `/home/user/myproject`
- Script path: `/home/user/myproject/parse_doc.py`
- Command: `python3 parse_doc.py` (run from `/home/user/myproject`)
- Output files created by the script:
  - `/home/user/myproject/output.md` — non-empty markdown text that contains the phrase `Quarterly Sales Report`.
  - `/home/user/myproject/output.log` — must contain:
    - A line in the format `trial_id: <trial_id>` where `<trial_id>` is the exact value read from `/logs/artifacts/trial_id`.
    - A line in the format `pages_parsed: <N>` where `<N>` is a positive integer.
- The script must run end to end without raising an exception; the script's exit code must be `0`.

