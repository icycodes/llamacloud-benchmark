# Parse a PDF Report to Markdown with LlamaParse

## Background
LlamaCloud is LlamaIndex's managed platform for production-grade document parsing and retrieval. Its `llama-cloud` Python SDK exposes LlamaParse, an agentic document parser that turns PDFs into clean, structured markdown that downstream RAG pipelines can consume.

In this task you must build a small parsing pipeline that takes a pre-existing PDF report and produces a markdown rendering of its first page using the LlamaCloud SDK.

## Requirements
- Write a Python script `parse_report.py` that uses the `llama-cloud` SDK (`from llama_cloud import LlamaCloud`) to:
  1. Upload the local PDF `report.pdf` to LlamaCloud with `purpose="parse"`.
  2. Submit a parse job using `tier="agentic"`, `version="latest"`, and `expand=["markdown"]`.
  3. Read the markdown text for the first page of the parsed result (i.e. `result.markdown.pages[0].markdown`).
  4. Write that markdown text to `output.md` in the same directory.
- The script must authenticate using the `LLAMA_CLOUD_API_KEY` environment variable (the SDK reads it automatically when `LlamaCloud()` is instantiated with no arguments).
- Running the script must produce a non-empty `output.md`.

## Implementation Guide
1. Change into the project directory `/home/user/llama_task`.
2. Create `parse_report.py` with logic similar to:
   ```python
   from llama_cloud import LlamaCloud

   client = LlamaCloud()  # reads LLAMA_CLOUD_API_KEY from the environment
   uploaded = client.files.create(file="./report.pdf", purpose="parse")
   result = client.parsing.parse(
       file_id=uploaded.id,
       tier="agentic",
       version="latest",
       expand=["markdown"],
   )
   first_page_md = result.markdown.pages[0].markdown
   with open("output.md", "w", encoding="utf-8") as f:
       f.write(first_page_md)
   ```
3. Execute the script with `python3 parse_report.py` from `/home/user/llama_task`. The script will block until LlamaCloud finishes parsing and returns the result.
4. Confirm that `output.md` was written.

## Constraints
- Project path: `/home/user/llama_task`
- Input file: `/home/user/llama_task/report.pdf` (already provided)
- Output file: `/home/user/llama_task/output.md`
- Script path: `/home/user/llama_task/parse_report.py`
- Use the `llama-cloud` SDK (the `LlamaCloud` client class). Do NOT call the REST API directly with `curl` or `requests`.
- The script must rely on `LLAMA_CLOUD_API_KEY` from the environment, not hardcoded.

## Integrations
- LlamaCloud (LlamaParse) — requires the `LLAMA_CLOUD_API_KEY` environment variable.
