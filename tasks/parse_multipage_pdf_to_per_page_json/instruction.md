# Parse a Multi-Page PDF to Per-Page JSON with LlamaParse

## Background
You are building an ingestion pipeline that needs page-level granularity for downstream chunking and citation. Plain combined Markdown is not enough — each page must remain individually addressable so that retrieval results can cite specific pages of the source document. The team uses LlamaCloud's LlamaParse service.

A pre-existing multi-page PDF is available at `/home/user/myproject/report.pdf` (3 pages). The Python packages `llama-cloud-services` and `llama-cloud` are pre-installed, and the API key is available via the `LLAMA_CLOUD_API_KEY` environment variable.

## Requirements
- Implement a Python script at `/home/user/myproject/parse_pages.py`.
- The script must call the LlamaCloud LlamaParse SDK (either `llama_cloud_services.LlamaParse` or the `llama_cloud.LlamaCloud` client) to parse `/home/user/myproject/report.pdf` with Markdown output.
- The script must write the per-page parsed Markdown to `/home/user/myproject/pages.json` as a JSON document with this exact top-level structure:
  ```json
  {
    "source": "report.pdf",
    "page_count": <total number of pages>,
    "pages": [
      {"page": 1, "markdown": "...page 1 markdown..."},
      {"page": 2, "markdown": "...page 2 markdown..."},
      {"page": 3, "markdown": "...page 3 markdown..."}
    ]
  }
  ```
  - `pages` MUST be a JSON list of objects.
  - Each object MUST have an integer `page` field that is 1-indexed and matches the page number, and a non-empty string `markdown` field with that page's parsed content.
  - `pages` MUST be ordered by ascending page number (1, 2, 3).
  - `page_count` MUST equal the length of `pages`.
- Running the script must produce the JSON file. Use `python3 parse_pages.py` as the entry point.

## Implementation Guide
1. Read the API key from the `LLAMA_CLOUD_API_KEY` environment variable (the SDK reads it automatically).
2. Parse `/home/user/myproject/report.pdf` with LlamaParse and request per-page Markdown output. Two valid approaches:
   - `llama_cloud_services.LlamaParse(result_type="markdown").load_data("/home/user/myproject/report.pdf")` returns one `Document` per page; use `documents[i].text` and 1-indexed page numbers.
   - `llama_cloud.LlamaCloud()` with `client.files.create(...)` and `client.parsing.parse(file_id=..., tier="agentic", version="latest", expand=["markdown"])`; the result exposes `result.markdown.pages`, each having a `markdown` attribute.
3. Build the JSON structure described above, ordered by ascending page number.
4. Write it to `/home/user/myproject/pages.json` using `json.dump(...)` with UTF-8 encoding.
5. Execute the script once so that `pages.json` exists when verification runs.

## Constraints
- Project path: /home/user/myproject
- Output file: /home/user/myproject/pages.json
- The script must perform a real LlamaParse API call — do not hardcode the Markdown content.
- Do not modify `/home/user/myproject/report.pdf`.
- The script must exit with code 0 when invoked as `python3 /home/user/myproject/parse_pages.py`.

## Integrations
- LlamaCloud (LlamaParse) — requires `LLAMA_CLOUD_API_KEY` set in the environment.
