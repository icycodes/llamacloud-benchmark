# Async Batch PDF Parsing with LlamaParse

## Background
You are building a data ingestion pipeline that needs to parse many PDF documents in parallel. LlamaCloud's LlamaParse service is the managed parser of choice. Your job is to write a Python script that asynchronously parses every PDF in a folder, saves the resulting Markdown for each document, and writes a summary log.

## Requirements
- Implement a Python script at `/home/user/myproject/parse_folder.py` that:
  - Reads `LLAMA_CLOUD_API_KEY` from the environment.
  - Discovers every `*.pdf` file in `/home/user/myproject/input_pdfs/` (non-recursive).
  - Uses `llama_parse.LlamaParse` (from the `llama-parse` PyPI package) with `result_type="markdown"` and processes the files concurrently via the asynchronous parsing API (e.g. `aload_data`).
  - For each input file `<name>.pdf`, writes the parsed Markdown to `/home/user/myproject/output_md/<name>.md`.
  - Writes a summary line per file to `/home/user/myproject/output.log`.
- The script must complete successfully when executed with `python3 parse_folder.py` from `/home/user/myproject`.

## Implementation Hints
- LlamaParse exposes async methods such as `aload_data` that fan out parse jobs concurrently and wait for all of them.
- Read the `trial_id` from `/logs/artifacts/trial_id` and include it in each log line so concurrent trials don't collide.
- The `documents` object returned by LlamaParse contains a `text` attribute holding the parsed Markdown.
- Make sure the output directory exists before writing files.
- Print any helpful debugging info to stdout, but the canonical results must go to the files listed above.

## Acceptance Criteria
- Project path: /home/user/myproject
- Log file: /home/user/myproject/output.log
- Command: `python3 parse_folder.py` executed from the project directory.
- The script reads the active `trial_id` from `/logs/artifacts/trial_id`.
- For every `<name>.pdf` in `/home/user/myproject/input_pdfs/`, a Markdown file `/home/user/myproject/output_md/<name>.md` must exist and contain non-empty Markdown content produced by LlamaParse.
- `/home/user/myproject/output.log` must contain, for every parsed file, a line in the exact format:
  `Parsed: <name>.pdf -> output_md/<name>.md (trial_id=<trial_id>)`
- The script must exit with status code 0.

