# Extract Tables from a Financial PDF with LlamaParse (Python)

## Background
You are building a small data-extraction prototype on **LlamaCloud** for a financial-analysis workflow. The team does not want the full Markdown of a quarterly report; they only want the **tables**, page by page, in a structured JSON file that another service can consume.

LlamaCloud's parsing service is exposed through the official Python SDK `llama-cloud` (entry class `LlamaCloud` from `llama_cloud`). Unlike a naive PDF text extractor, LlamaParse preserves table structure and returns per-page Markdown — including pipe-style Markdown tables — when called with `expand=["markdown"]` and `output_options.markdown.tables.output_tables_as_markdown=True`.

The `llama-cloud` Python SDK is already installed, the `LLAMA_CLOUD_API_KEY` environment variable is set, and a multi-page sample report is pre-staged at `/home/user/myproject/report.pdf`. The report is titled `FY2024 Quarterly Performance Report` and contains **two tables**:
- Page 1 has a `Revenue by Product` table with columns `Product`, `Q1 Revenue (USD)`, `Q2 Revenue (USD)` and rows for `Widget A`, `Widget B`, `Service Plan`.
- Page 2 has a `Regional Sales` table with columns `Region`, `Q1 Units`, `Q2 Units` and rows for `North America`, `Europe`, `Asia Pacific`.

Because this task may run multiple times concurrently against the same LlamaCloud account, you must read the `trial_id` from `/logs/artifacts/trial_id` and tag the output artifacts with it (the parsing service itself is stateless for a single parse call, so no global resource needs to carry the trial id — only your output files do).

## Requirements
Write a Python script at `/home/user/myproject/extract_tables.py` that:
- Reads the `trial_id` value from `/logs/artifacts/trial_id`.
- Uses the `llama_cloud` Python SDK to upload `/home/user/myproject/report.pdf` and then runs a parse job that returns per-page Markdown.
- Extracts, for every page returned by LlamaParse, any **Markdown tables** present on that page (a Markdown table is a contiguous block of lines that start with `|` and includes a header-separator row like `|---|---|---|`).
- Writes a single JSON file to `/home/user/myproject/tables.json` with the exact top-level shape:
  ```json
  {
    "trial_id": "<trial_id>",
    "num_pages": <integer>,
    "num_tables": <integer>,
    "tables": [
      {"page": <integer>, "markdown": "<the markdown table as a single string, including the header separator row>"},
      ...
    ]
  }
  ```
  where:
  - `trial_id` is the exact value read from `/logs/artifacts/trial_id`.
  - `num_pages` is the total number of pages returned by LlamaParse.
  - `num_tables` is the length of the `tables` array.
  - Each entry in `tables` corresponds to one Markdown table found on the document, in document order. `page` is 1-indexed and matches the LlamaParse page numbering.
- Writes a plain-text log to `/home/user/myproject/output.log` containing at minimum these three lines (one fact per line):
  - `trial_id: <trial_id>`
  - `num_pages: <N>` — total pages returned by LlamaParse.
  - `num_tables: <M>` — number of Markdown tables found.
- The script must run end to end with `python3 extract_tables.py` from `/home/user/myproject` and exit with status code `0`.

## Implementation Hints
- The modern Python SDK entrypoint is `from llama_cloud import LlamaCloud` and then `client = LlamaCloud()`. The client reads `LLAMA_CLOUD_API_KEY` from the environment automatically.
- Upload the PDF with `client.files.create(file="./report.pdf", purpose="parse")` and grab `file.id`.
- Run a synchronous parse with `client.parsing.parse(file_id=file.id, tier="agentic", version="latest", expand=["markdown"], output_options={"markdown": {"tables": {"output_tables_as_markdown": True}}})`. The call blocks until the job finishes and returns a result object whose `.markdown.pages` field is a list of objects with `.page_number` and `.markdown` attributes.
- A simple way to identify a Markdown table inside a page's Markdown string is: find a block of consecutive non-blank lines that all start with `|` and contains at least one line whose cells are made of dashes (the header-separator row like `|---|---|`).
- Use `json.dump(...)` with `indent=2` (or any valid JSON formatting) when writing `tables.json`.

## Acceptance Criteria
- Project path: `/home/user/myproject`
- Script path: `/home/user/myproject/extract_tables.py`
- Command: `python3 extract_tables.py` (run from `/home/user/myproject`)
- The script must exit with return code `0`.
- Output files created by the script:
  - `/home/user/myproject/tables.json` — must be valid JSON with the top-level shape described above:
    - `trial_id` (string) equal to the value at `/logs/artifacts/trial_id`.
    - `num_pages` (integer, >= 1).
    - `num_tables` (integer, >= 2 — the report contains at least two tables).
    - `tables` (array) with `num_tables` entries; each entry has integer `page` (>= 1) and string `markdown` that:
      - Contains at least one line starting with `|`.
      - Contains a Markdown header-separator row matching the pattern `\|\s*[-: ]+\s*\|` (i.e., a `|---|---|`-style row).
    - Across all `tables[*].markdown` strings combined, the following substrings must appear (case-insensitive):
      - `Widget A`
      - `Service Plan`
      - `North America`
      - `Asia Pacific`
  - `/home/user/myproject/output.log` — must contain:
    - A line matching `trial_id: <trial_id>` where `<trial_id>` equals the value in `/logs/artifacts/trial_id`.
    - A line matching `num_pages: <N>` where `<N>` is a positive integer (>= 1).
    - A line matching `num_tables: <M>` where `<M>` is a positive integer (>= 2).

