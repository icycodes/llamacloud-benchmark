# Parse a Multi-Page PDF into Structured JSON with LlamaParse (Python)

## Background
LlamaCloud's `LlamaParse` parser supports several output modes. While `result_type="markdown"` returns clean markdown documents, `result_type="json"` (used together with `parser.get_json_result(...)`) returns a much richer structured representation that contains, per page, the page number, the extracted text, the markdown rendering, and the list of structured items (headings, paragraphs, tables, etc.). This JSON view is the right primitive when a downstream pipeline wants programmatic access to the page-level structure instead of a single flat markdown blob.

In this task you must build a small Python program that uses `LlamaParse` in JSON mode to parse a deterministic three-page PDF and write a structured per-page JSON manifest that a downstream system could consume directly.

The task workspace `/home/user/parse_json_task` is pre-seeded with a three-page PDF at `/home/user/parse_json_task/sample.pdf` (generated at image build time, identical across runs). Every page contains exactly one distinct marker phrase and one quarterly-revenue sentence so the manifest can be verified deterministically:

- Page `1`: `JSON-Mode-Page-One` and the sentence `The total revenue in Q1 was $500,000.`
- Page `2`: `JSON-Mode-Page-Two` and the sentence `The total revenue in Q2 was $750,000.`
- Page `3`: `JSON-Mode-Page-Three` and the sentence `The total revenue in Q3 was $1,000,000.`

## Requirements
- Read the current `trial_id` from `/logs/artifacts/trial_id`.
- Write a Python script `parse_to_json.py` in `/home/user/parse_json_task` that:
  - Authenticates against LlamaCloud using the `LLAMA_CLOUD_API_KEY` environment variable.
  - Uses the official LlamaParse Python SDK (e.g. `from llama_cloud_services import LlamaParse` or `from llama_parse import LlamaParse`) configured with `result_type="json"` to parse `sample.pdf`.
  - Calls `parser.get_json_result(...)` (the JSON-mode entry point) to obtain the structured per-page payload returned by LlamaParse. The returned object is a list with one element per parsed PDF; the element exposes a `job_id` and a `pages` list whose entries contain at least the keys `page`, `text`, and `md`.
  - Writes a JSON manifest to `/home/user/parse_json_task/output.json` (UTF-8, JSON-pretty-printed with `indent=2`) with the shape:
    ```json
    {
      "trial_id": "<trial_id from /logs/artifacts/trial_id>",
      "job_id": "<LlamaParse job id>",
      "page_count": 3,
      "pages": [
        {"page": 1, "text": "<extracted page 1 text>", "markdown": "<extracted page 1 markdown>"},
        {"page": 2, "text": "<extracted page 2 text>", "markdown": "<extracted page 2 markdown>"},
        {"page": 3, "text": "<extracted page 3 text>", "markdown": "<extracted page 3 markdown>"}
      ]
    }
    ```
    Entries in `pages` must be sorted by ascending `page` number. Each `text` and `markdown` value must be the corresponding string returned by LlamaParse for that page.
  - Writes a companion log file `/home/user/parse_json_task/output.log` containing the lines required in the Acceptance Criteria below so the verifier can correlate the produced artifacts with the trial and the LlamaParse job.
- The script must run end-to-end with `python3 parse_to_json.py` from `/home/user/parse_json_task` and exit with status code `0`.

## Implementation Hints
- The LlamaParse Python SDK reads `LLAMA_CLOUD_API_KEY` from the environment automatically when the variable is set; you do not need to pass `api_key=...` explicitly.
- The relevant constructor flag is `result_type="json"`. With that setting, the call `parser.get_json_result("./sample.pdf")` returns a list of dictionaries. Each dictionary describes one parsed file and contains at least `job_id` and `pages`. Inside `pages`, each entry has `page` (1-indexed), `text`, and `md`.
- Use the standard library `json` module to serialize the manifest and write it with UTF-8 encoding.
- Read `trial_id` once at the top of the script and embed it in both the JSON manifest and the log file.

## Acceptance Criteria
- Project path: `/home/user/parse_json_task`
- Source PDF: `/home/user/parse_json_task/sample.pdf`
- Script path: `/home/user/parse_json_task/parse_to_json.py`
- JSON manifest: `/home/user/parse_json_task/output.json`
- Log file: `/home/user/parse_json_task/output.log`
- Command: `python3 /home/user/parse_json_task/parse_to_json.py` (run from `/home/user/parse_json_task`).
  - The command must exit with status code `0`.
- LlamaParse usage:
  - `parse_to_json.py` must import `LlamaParse` from either `llama_cloud_services` or `llama_parse` (the source must contain the literal substring `from llama_cloud_services import` or `from llama_parse import`).
  - The source must contain the literal substring `result_type` configured to the JSON output mode (e.g. `result_type="json"`).
  - The source must call `get_json_result` (so the JSON-mode entry point is actually used).
- The JSON manifest `/home/user/parse_json_task/output.json` must:
  - Be a non-empty UTF-8 file that parses with `json.load(...)` into a single object.
  - Contain top-level keys `trial_id`, `job_id`, `page_count`, and `pages`.
  - `trial_id` must equal the value read from `/logs/artifacts/trial_id`.
  - `page_count` must be the integer `3`.
  - `pages` must be a JSON array of length `3` whose entries are sorted by ascending `page`.
  - Each entry in `pages` must be a JSON object containing the keys `page`, `text`, and `markdown`.
  - The `page` values must be exactly `1`, `2`, `3` in order.
  - The `text` field of each page must contain the marker phrase for that page (`JSON-Mode-Page-One`, `JSON-Mode-Page-Two`, `JSON-Mode-Page-Three` respectively) and the page's quarterly-revenue dollar value (`$500,000`, `$750,000`, `$1,000,000` respectively).
- The log file `/home/user/parse_json_task/output.log` must contain:
  - A line of the form `Trial id: <trial_id>` where `<trial_id>` is the value read from `/logs/artifacts/trial_id`.
  - A line of the form `Job id: <job_id>` where `<job_id>` is the same LlamaParse job id stored in `output.json`.
  - A line of the form `Page count: 3`.

