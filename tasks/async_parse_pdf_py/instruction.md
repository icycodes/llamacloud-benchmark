# Parse a PDF Asynchronously with LlamaParse (Python `AsyncLlamaCloud`)

## Background
You are working at `/home/user/myproject`, which already contains a sample PDF named `sample.pdf` (it embeds the literal text `Hello LlamaParse - Harbor Test Document` on a single page). Your job is to build a small command-line utility that uses the **asynchronous** [LlamaCloud Python SDK](https://developers.llamaindex.ai/llamaparse/parse/getting_started/) (the `llama-cloud` package, version 2.1 or newer) to parse a PDF document via the managed LlamaParse service and persist the parsed markdown content to disk.

Unlike the synchronous `LlamaCloud` client, this task **MUST** be implemented with the asynchronous client `AsyncLlamaCloud`. The script must define an async coroutine that performs the upload and parse using `await`, and the program entry-point must drive that coroutine with `asyncio.run(...)`.

The SDK is already installed in the environment and the `LLAMA_CLOUD_API_KEY` environment variable is configured. You do NOT need to handle authentication explicitly — the SDK reads the API key from the environment automatically.

## Requirements
- Implement a Python CLI named `async_parse.py` at `/home/user/myproject/async_parse.py`.
- The script must accept exactly two command-line arguments:
  - `--input <path>`: the path to the local PDF file to parse.
  - `--output <path>`: the path where the parsed markdown should be written.
- The script MUST use the **asynchronous** LlamaCloud Python SDK client: `from llama_cloud import AsyncLlamaCloud`.
- The script MUST define an `async def` coroutine (e.g., `async def main():`) that contains all `await`-ed SDK calls, and the program entry-point MUST drive it with `asyncio.run(main())`.
- Validate that the `--input` file exists before uploading. If it does not, print an error message to stderr and exit with a **non-zero** status code (do NOT silently succeed when the input file is missing).
- Inside the coroutine:
  - Upload the input file with `purpose="parse"` using `await client.files.create(file=<input_path>, purpose="parse")`.
  - Trigger a parsing job using `await client.parsing.parse(file_id=..., tier="agentic", version="latest", expand=["markdown"])`. The SDK awaits until the job finishes and returns the full result.
- After the job completes, write the **per-page markdown joined into a single document** to the `--output` file. Pages must be joined with two consecutive newline characters (`\n\n`) between adjacent pages, in their original page order. Use UTF-8 encoding for the output file.
- Print a single line to stdout in the exact format: `Parsed <N> pages asynchronously` where `<N>` is the number of pages returned by the parse job (i.e., `len(result.markdown.pages)`).
- The script must exit with status code `0` on success.

## Implementation Guide
1. Create `/home/user/myproject/async_parse.py`.
2. Use `argparse` (standard library) to parse `--input` and `--output`.
3. Check existence of `--input` with `os.path.isfile(...)`. If missing, write an error message to `sys.stderr` and `sys.exit(1)`.
4. Import the async client: `from llama_cloud import AsyncLlamaCloud`.
5. Define `async def main(input_path: str, output_path: str) -> int:` that:
   - Instantiates the client: `client = AsyncLlamaCloud()` (it reads `LLAMA_CLOUD_API_KEY` from the environment).
   - Uploads the file: `file = await client.files.create(file=input_path, purpose="parse")`.
   - Submits the parse job: `result = await client.parsing.parse(file_id=file.id, tier="agentic", version="latest", expand=["markdown"])`.
   - Joins per-page markdown: `"\n\n".join(p.markdown for p in result.markdown.pages)`.
   - Writes the joined string to `output_path` (UTF-8).
   - Prints `Parsed <N> pages asynchronously` where `<N>` is `len(result.markdown.pages)`.
   - Returns `0` on success.
6. Drive the coroutine: `sys.exit(asyncio.run(main(args.input, args.output)))`.

## Acceptance Criteria
- Project path: /home/user/myproject
- Script path: /home/user/myproject/async_parse.py
- Command: `python3 async_parse.py --input <pdf_path> --output <output_md_path>`
- Input argument format: `--input <path_to_pdf>` and `--output <path_to_output_markdown_file>`
- Expected command stdout: includes exactly one line `Parsed <N> pages asynchronously` where `<N>` is the page count returned by LlamaParse (the provided `sample.pdf` has exactly 1 page, so the line must be exactly `Parsed 1 pages asynchronously`).
- The output markdown file must be created at the path specified by `--output` and must contain the per-page markdown joined with `\n\n` between pages.
- The script must import the **asynchronous** client class `AsyncLlamaCloud` from `llama_cloud` (a line matching `from llama_cloud import AsyncLlamaCloud`).
- The script must define at least one `async def` function and drive it with `asyncio.run(...)`. The string `asyncio.run` must appear in the source.
- The script must pass `tier="agentic"`, `version="latest"`, and `expand` including `"markdown"` to `client.parsing.parse`.
- The script must succeed (exit code 0) when given a valid PDF and a valid `LLAMA_CLOUD_API_KEY`.
- The script must exit with a non-zero status code when `--input` refers to a non-existent file.

