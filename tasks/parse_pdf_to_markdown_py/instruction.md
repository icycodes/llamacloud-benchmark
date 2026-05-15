# Parse a PDF Report to Markdown with LlamaParse (Python)

## Background
You are given a financial PDF report at `/home/user/parse_task/sample.pdf`. The report contains a title, a paragraph of text, and a small table. You need to convert this PDF into clean markdown using LlamaCloud's LlamaParse service so that the output preserves the headings, body text, and tabular structure for use in a downstream RAG pipeline.

## Requirements
- Write a Python script `parse.py` in `/home/user/parse_task` that authenticates against LlamaCloud using the `LLAMA_CLOUD_API_KEY` environment variable.
- Use the official LlamaCloud Python SDK (`llama-cloud` package, i.e. `from llama_cloud import LlamaCloud`) to upload `sample.pdf` and run a parse job.
- Retrieve the parsed markdown for the document and write the full markdown text (concatenation of all pages, separated by blank lines) to `/home/user/parse_task/output.md`.
- The script must run end-to-end with `python3 parse.py` and exit with status code `0` on success.

## Implementation Hints
- The LlamaCloud Python SDK reads `LLAMA_CLOUD_API_KEY` automatically when you instantiate `LlamaCloud()`.
- Use `client.files.create(file=..., purpose="parse")` to upload the PDF, then `client.parsing.parse(file_id=..., tier="agentic", version="latest", expand=["markdown"])` to run the parse job. The SDK polls for completion.
- The result object exposes the parsed markdown per page; iterate over the pages and join their markdown content.
- You do not need to call any other LlamaCloud endpoints (no index creation is required for this task).

## Acceptance Criteria
- Project path: `/home/user/parse_task`
- Script path: `/home/user/parse_task/parse.py`
- Output file: `/home/user/parse_task/output.md`
- Command: `python3 /home/user/parse_task/parse.py`
  - The command must exit with status code `0`.
- The output file must exist and be non-empty UTF-8 text.
- The markdown content in `/home/user/parse_task/output.md` must faithfully reflect the source PDF, including:
  - The report title heading text.
  - The body paragraph that mentions the total revenue figure.
  - A markdown representation of the revenue table that lists every department row from the source PDF.

