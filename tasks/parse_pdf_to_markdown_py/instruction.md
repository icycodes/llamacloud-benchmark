# Parse a PDF to Markdown with LlamaCloud (Python)

## Background
LlamaCloud is the managed RAG platform from LlamaIndex. Its Parse service (LlamaParse) turns visually rich documents like PDFs into clean, layout-aware markdown that can be fed into downstream LLM pipelines. In this task you will use the official `llama-cloud` Python SDK to upload a small PDF, run a parse job against LlamaCloud, and persist the resulting markdown to disk so the rest of the pipeline can consume it.

The PDF you need to parse is already on disk at `/home/user/myproject/quarterly_report.pdf`. It is a one-page synthetic report whose body contains the title `ACME CORP QUARTERLY REPORT`, a sentence stating `Total revenue for Q3 was 12345 USD.`, and a short paragraph about the company's outlook.

A LlamaCloud API key is already exported as the `LLAMA_CLOUD_API_KEY` environment variable.

## Requirements
- Write a Python script at `/home/user/myproject/parse_report.py` that, when executed, performs the following one-off job:
  - Uploads `/home/user/myproject/quarterly_report.pdf` to LlamaCloud using the official Python SDK.
  - Runs a parse job against the uploaded file and retrieves the markdown output.
  - Concatenates the markdown for every page of the document into a single string and writes it to `/home/user/myproject/output.md` (UTF-8 encoded).
  - Writes a structured log line to `/home/user/myproject/parse.log` indicating success and the LlamaCloud parse job identifier.
- Run the script once so that `output.md` and `parse.log` are populated before verification begins.

## Implementation Hints
- The current SDK is the `llama-cloud` Python package; install it with `pip3 install --break-system-packages llama-cloud`.
- The high-level entry point is `from llama_cloud import LlamaCloud`. The client automatically reads `LLAMA_CLOUD_API_KEY` from the environment.
- Use `client.files.create(file=..., purpose="parse")` to upload the PDF and grab the returned `id`. Pass that id to `client.parsing.parse(...)` with `expand=["markdown"]` to retrieve the markdown payload synchronously.
- The markdown payload exposes one entry per page (e.g. `result.markdown.pages[i].markdown`). Join them with blank lines before writing to disk so multi-page documents are not truncated.
- LlamaParse needs to know the file type. When uploading from disk this is taken from the file extension, so make sure you pass the real PDF path (or, if you use bytes, supply the original file name).

## Acceptance Criteria
- Project path: /home/user/myproject
- Script path: /home/user/myproject/parse_report.py
- Log file: /home/user/myproject/parse.log
- Markdown output file: /home/user/myproject/output.md
- The script must be runnable as `python3 /home/user/myproject/parse_report.py` and must exit with status code 0.
- After running the script:
  - `/home/user/myproject/output.md` must exist, be non-empty, and contain the parsed markdown for the PDF (every page concatenated).
  - `/home/user/myproject/parse.log` must contain a line of the form: `Parse job ID: <job_id>` where `<job_id>` is the identifier returned by LlamaCloud for the parse job.
  - `/home/user/myproject/parse.log` must contain a line of the form: `Parsed file: /home/user/myproject/quarterly_report.pdf`.

