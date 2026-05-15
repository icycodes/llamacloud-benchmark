# Parse a PDF Document to Markdown with LlamaParse (Python)

## Background
You are working at `/home/user/myproject`, which already contains a sample PDF named `sample.pdf`. Your job is to build a small command-line utility that uses the [LlamaCloud Python SDK](https://developers.llamaindex.ai/llamaparse/parse/getting_started/) (the `llama-cloud` package, version 2.1 or newer) to parse a PDF document via the managed LlamaParse service and persist the parsed markdown content to disk.

The SDK is already installed in the environment and the `LLAMA_CLOUD_API_KEY` environment variable is configured. You do NOT need to handle authentication explicitly — the SDK reads the API key from the environment automatically.

## Requirements
- Implement a Python CLI named `parse.py` at `/home/user/myproject/parse.py`.
- The script must accept exactly two command-line arguments:
  - `--input <path>`: the path to the local PDF file to parse.
  - `--output <path>`: the path where the parsed markdown should be written.
- The script must use the **`llama-cloud`** Python SDK (`from llama_cloud import LlamaCloud`).
- Upload the input file with `purpose="parse"` and then run a parsing job using **tier `cost_effective`** and **version `latest`**. Request markdown output via the `expand` parameter.
- After the job completes, write the **per-page markdown joined into a single document** to the `--output` file. Pages must be joined with two consecutive newline characters (`\n\n`) between adjacent pages, in their original page-order.
- Print a single line to stdout in the exact format: `Parsed <N> pages` where `<N>` is the number of pages returned by the parse job.
- The script must exit with status code `0` on success.

## Implementation Guide
1. Initialize the project at `/home/user/myproject`.
2. Use `argparse` (standard library) to parse `--input` and `--output` arguments.
3. Import `LlamaCloud` from `llama_cloud` and instantiate a client (no arguments — it reads `LLAMA_CLOUD_API_KEY` from the environment).
4. Upload the file via `client.files.create(file=<input_path>, purpose="parse")`.
5. Trigger a parse job via `client.parsing.parse(file_id=..., tier="cost_effective", version="latest", expand=["markdown"])`. The SDK blocks until the job completes.
6. Iterate over `result.markdown.pages` (each page exposes a `markdown` attribute), join the per-page markdown strings with `\n\n`, and write the joined string to `--output`.
7. Print `Parsed <N> pages` to stdout where `<N>` equals `len(result.markdown.pages)`.

## Acceptance Criteria
- Project path: /home/user/myproject
- Script path: /home/user/myproject/parse.py
- Command: `python3 parse.py --input <pdf_path> --output <output_md_path>`
- Input argument format: `--input <path_to_pdf>` and `--output <path_to_output_markdown_file>`
- Expected command output: stdout must include exactly one line `Parsed <N> pages` where `<N>` is the page count returned by LlamaParse.
- The output markdown file must be created at the path specified by `--output` and must contain the per-page markdown joined with `\n\n` between pages.
- The script must use the `llama-cloud` Python SDK with `tier="cost_effective"` and `version="latest"`.
- The script must succeed (exit code 0) when given a valid PDF and a valid `LLAMA_CLOUD_API_KEY`.

