# Extract Every Table from a Multi-Page PDF to CSV with LlamaParse

## Background
You are building a financial data pipeline. Analysts need every table from a multi-page report exported as standalone CSV files (one CSV per table) so they can load them directly into pandas / a data warehouse. The team has chosen LlamaCloud's LlamaParse service because it returns structured `items` per page (headings, paragraphs, tables, etc.), so tables can be found and exported deterministically.

A pre-existing multi-page PDF lives at `/home/user/myproject/quarterly_report.pdf`. It has 2 pages and each page contains a clearly tabular block:
- Page 1: a quarterly revenue table with columns `Quarter`, `Revenue`, `Profit`.
- Page 2: an employee headcount table with columns `Department`, `Headcount`, `Open Roles`.

The Python packages `llama-cloud-services` and `llama-cloud` are already installed in the environment, and the API key is configured via the `LLAMA_CLOUD_API_KEY` environment variable.

## Requirements
- Implement a Python script at `/home/user/myproject/extract_tables.py`.
- The script must use the LlamaCloud LlamaParse SDK (`llama_cloud.LlamaCloud` is recommended, but `llama_cloud_services.LlamaParse` is also acceptable) to parse `/home/user/myproject/quarterly_report.pdf` with the `items` view available (e.g. `tier="agentic"`, `version="latest"`, `expand=["items", "markdown"]`).
- The script must walk every parsed page, collect every element whose type is `"table"`, and export each table to its own CSV file under the directory `/home/user/myproject/tables/`. Each CSV filename MUST follow the deterministic pattern `table_p{page:03d}_{i}.csv`, where `page` is the 1-indexed page the table was found on and `i` is the 0-indexed order of the table within that page (`table_p001_0.csv`, `table_p002_0.csv`, ...).
- The script must also write a summary JSON file to `/home/user/myproject/tables_summary.json` with this exact top-level structure:
  ```json
  {
    "source": "quarterly_report.pdf",
    "table_count": <total number of tables found>,
    "tables": [
      {"page": <int>, "file": "table_pNNN_M.csv", "rows": <int>, "cols": <int>}
    ]
  }
  ```
  - `tables` MUST be a JSON list ordered by `(page ASC, file ASC)`.
  - Each object MUST have an integer `page` (1-indexed), a string `file` matching the CSV filename written in `/home/user/myproject/tables/`, an integer `rows` (number of rows in that table, including header row if present), and an integer `cols` (number of columns).
  - `table_count` MUST equal the length of `tables`.
- Running the script must produce the CSV files and the summary JSON. Use `python3 extract_tables.py` as the entry point.

## Implementation Guide
1. Read the API key from the `LLAMA_CLOUD_API_KEY` environment variable (the SDK reads it automatically).
2. Upload `/home/user/myproject/quarterly_report.pdf` via `client.files.create(file="...", purpose="parse")` and call `client.parsing.parse(file_id=..., tier="agentic", version="latest", expand=["items", "markdown"])`.
3. Iterate `result.items.pages`; for each `page`, iterate `page.items`. Tables have `getattr(item, "type", None) == "table"` and expose a `csv` string field plus a `rows` field (a list of lists).
4. Make sure the directory `/home/user/myproject/tables/` exists, then write `item.csv` to `/home/user/myproject/tables/table_p{page.page_number:03d}_{i}.csv` (UTF-8, no BOM). `i` is the order of the table within that page (start at 0).
5. Compute the row count and column count for each table from `item.rows` (or by re-parsing the CSV with `csv.reader`) and append an entry to the summary list.
6. Sort the summary list by `(page, file)` and serialize it as JSON to `/home/user/myproject/tables_summary.json` using `json.dump(... , indent=2)`.
7. Execute the script once so that the output files exist when verification runs.

## Constraints
- Project path: /home/user/myproject
- Output directory: /home/user/myproject/tables/
- Summary file: /home/user/myproject/tables_summary.json
- The script must perform a real LlamaParse API call — do not hardcode CSV contents, do not hand-write CSV from prior knowledge of the PDF.
- Do not modify `/home/user/myproject/quarterly_report.pdf`.
- The script must exit with code 0 when invoked as `python3 /home/user/myproject/extract_tables.py`.

## Integrations
- LlamaCloud (LlamaParse) — requires `LLAMA_CLOUD_API_KEY` set in the environment.
