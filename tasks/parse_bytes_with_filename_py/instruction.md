# Parse PDF Bytes with LlamaParse Using `file_name` Metadata (Python)

## Background
In many real-world pipelines, PDFs do not arrive as files on disk — they come through an upload endpoint, a queue, an S3 stream, or some other source that yields raw bytes. LlamaCloud's `LlamaParse` parser supports this directly through the `load_data` API, but when you pass raw bytes (or a binary file object) instead of a path, the parser cannot infer the document type from a file extension. You **must** supply a hint via `extra_info={"file_name": "..."}`; otherwise `LlamaParse.load_data` raises a `ValueError` with the message `file_name must be provided in extra_info when passing bytes` and no parsing is performed.

In this task you must build a small Python program that takes a directory full of PDFs, loads each one **as raw bytes** (no file paths), parses every PDF with `LlamaParse` using the `file_name`-in-`extra_info` pattern, and writes per-document markdown output plus a manifest summarizing what was parsed.

The task workspace `/home/user/parse_bytes_task` is pre-seeded with three deterministic PDFs in `/home/user/parse_bytes_task/docs/`:
- `alpha_report.pdf` — a short status report.
- `beta_invoice.pdf` — a tiny one-line invoice.
- `gamma_memo.pdf` — a brief internal memo.
Each PDF contains a clearly identifiable headline string that makes the parsed output easy to audit.

## Requirements
- Write a Python script `parse_bytes.py` in `/home/user/parse_bytes_task` that authenticates against LlamaCloud using the `LLAMA_CLOUD_API_KEY` environment variable.
- Use the official `LlamaParse` client from `llama_cloud_services` (i.e. `from llama_cloud_services import LlamaParse`), configured with `result_type="markdown"`.
- For **every** PDF inside `/home/user/parse_bytes_task/docs/`:
  - Read the file into memory as raw `bytes` (use Python's built-in file I/O — do not pass the path string to `load_data`).
  - Call `parser.load_data(file_bytes, extra_info={"file_name": <basename>})` where `<basename>` is the original PDF file name (for example `alpha_report.pdf`).
  - Concatenate the `.text` of every returned `Document` (joined with a blank line between pages) and write the result to `/home/user/parse_bytes_task/output/<stem>.md`, where `<stem>` is the file name without the `.pdf` extension (for example `/home/user/parse_bytes_task/output/alpha_report.md`).
- After processing every file, write a manifest file at `/home/user/parse_bytes_task/output/manifest.json` whose top-level value is a JSON object of the form:
  ```json
  {
    "parsed": [
      {"file_name": "alpha_report.pdf", "output": "output/alpha_report.md", "chars": <int>},
      {"file_name": "beta_invoice.pdf", "output": "output/beta_invoice.md", "chars": <int>},
      {"file_name": "gamma_memo.pdf",   "output": "output/gamma_memo.md",   "chars": <int>}
    ]
  }
  ```
  - `chars` is the integer character count of the corresponding markdown file's contents.
  - The `parsed` list must contain exactly one entry per PDF in `docs/`, with `file_name` being the original PDF name.
  - Entries must be sorted alphabetically by `file_name` (so `alpha_report.pdf` comes first).
- The script must run end-to-end with `python3 parse_bytes.py` and exit with status code `0` on success.

## Implementation Hints
- `LlamaParse` (from `llama_cloud_services`) reads `LLAMA_CLOUD_API_KEY` automatically when instantiated with no `api_key` argument.
- When you pass raw bytes to `parser.load_data`, the parser inspects the file extension of `extra_info["file_name"]` to pick the right parsing strategy — forgetting the `file_name` key will make the SDK raise immediately with `file_name must be provided in extra_info when passing bytes`.
- `parser.load_data` returns a list of `Document` objects; each `Document` exposes the parsed markdown via the `.text` attribute.
- Iterate over the directory deterministically (for example with `sorted(os.listdir(...))`) so the manifest order is stable.
- Make sure to create the `/home/user/parse_bytes_task/output/` directory before writing files into it.

## Acceptance Criteria
- Project path: `/home/user/parse_bytes_task`
- Input directory: `/home/user/parse_bytes_task/docs` (contains `alpha_report.pdf`, `beta_invoice.pdf`, `gamma_memo.pdf`).
- Script path: `/home/user/parse_bytes_task/parse_bytes.py`
- Output directory: `/home/user/parse_bytes_task/output`
- Manifest file: `/home/user/parse_bytes_task/output/manifest.json`
- Per-document markdown files: `/home/user/parse_bytes_task/output/<stem>.md` for each PDF in `docs/`.
- Command: `python3 /home/user/parse_bytes_task/parse_bytes.py`
  - The command must exit with status code `0`.
- `parse_bytes.py` must import `LlamaParse` from `llama_cloud_services` and must call `load_data` with raw `bytes` (not a file path) plus `extra_info={"file_name": ...}`.
- Each generated markdown file must be a non-empty UTF-8 file whose contents reflect the source PDF (it must include the document's headline text from the source PDF).
- `manifest.json` schema:
  ```json
  {
    "parsed": [
      {"file_name": "<original.pdf>", "output": "output/<stem>.md", "chars": <int>}
    ]
  }
  ```
  - The top-level object must contain a `parsed` array of length equal to the number of PDFs in `docs/`.
  - Entries are sorted alphabetically by `file_name`.
  - For each entry, `chars` must equal the actual character count (in characters, not bytes) of the contents of the file referenced by `output`.

