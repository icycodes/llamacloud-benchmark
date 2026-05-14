# LlamaParse Offline Parse Plan Builder

## Background
Before sending documents to LlamaParse for production parsing, teams routinely build a local pre-flight "parse plan" so they can audit which files will be uploaded, compute content hashes for change detection, and verify that the SDK is wired up correctly. A common friction point with LlamaParse is forgetting to provide `extra_info={"file_name": ...}` when feeding raw bytes into the parser; the parser uses the extension contained in `file_name` to pick the correct parsing strategy. Building a manifest up front prevents this entire class of error.

You must build a small, fully offline Python CLI utility that uses the `llama_cloud_services.LlamaParse` SDK class to capture the parser configuration, then scans an input directory to produce a JSON parse plan. The script must NOT make any network calls.

## Requirements
- Implement a Python CLI script `parse_plan.py` that instantiates `LlamaParse` from the `llama_cloud_services` package and uses its configuration attributes to populate the output plan.
- The CLI must accept the following arguments:
  - `--input-dir` (required): path to a directory of source documents.
  - `--output` (required): path to the JSON plan file to write.
  - `--result-type` (optional, default `markdown`): forwarded to `LlamaParse(result_type=...)`. Must accept one of `markdown` or `text`.
  - `--num-workers` (optional, integer, default `2`): forwarded to `LlamaParse(num_workers=...)`.
  - `--language` (optional, default `en`): forwarded to `LlamaParse(language=...)`.
- The script must instantiate the parser like this (no other arguments are needed):
  ```python
  parser = LlamaParse(
      api_key="llx-dummy-offline-key",
      result_type=args.result_type,
      num_workers=args.num_workers,
      language=args.language,
  )
  ```
  The literal `api_key="llx-dummy-offline-key"` is required because no network calls are made; it merely satisfies the SDK constructor.
- The script must enumerate files in `--input-dir` non-recursively and include only files with one of these supported extensions (case-insensitive match): `.pdf`, `.docx`, `.pptx`, `.txt`, `.md`, `.html`.
- For each included file, the script must compute:
  - `file_name`: the basename of the file (e.g., `notes.md`).
  - `path`: the absolute path of the file.
  - `size_bytes`: integer file size in bytes from the filesystem.
  - `sha256`: lowercase hex digest of the file's full byte contents using SHA-256.
  - `extra_info`: a dict literally equal to `{"file_name": <basename>}` (this is the exact shape LlamaParse requires for byte-stream parsing).
- The script must produce a JSON file at `--output` with this exact top-level shape (no extra keys):
  ```json
  {
    "parser_config": {
      "result_type": "<resolved result_type>",
      "num_workers": <resolved num_workers>,
      "language": "<resolved language>"
    },
    "files": [
      {
        "file_name": "<basename>",
        "path": "<absolute path>",
        "size_bytes": <int>,
        "sha256": "<lowercase hex digest>",
        "extra_info": {"file_name": "<basename>"}
      }
    ]
  }
  ```
- The `files` array MUST be sorted alphabetically by `file_name` (case-sensitive `sorted()` order).
- On success, the script must print exactly one line to stdout in this exact format and then exit with status `0`:
  `Parse plan created with <N> files at <output_path>`
  where `<N>` is the integer count of files included and `<output_path>` is the absolute output path as provided by `--output`.
- If `--input-dir` does not exist or is not a directory, the script must:
  - print the message `Error: input directory not found: <input_dir>` to stderr,
  - NOT write any output file,
  - exit with a non-zero status code.
- The script MUST NOT make any outbound HTTP calls.

## Implementation Guide
1. The project directory `/home/user/parse_planner` already exists and contains an `inputs/` subdirectory pre-populated with sample files. Do NOT delete or modify those files.
2. Create the script at `/home/user/parse_planner/parse_plan.py`.
3. Use `argparse` for argument parsing.
4. Import the SDK class with: `from llama_cloud_services import LlamaParse`.
5. Instantiate the parser exactly as shown in the Requirements section, then read back `parser.result_type`, `parser.num_workers`, and `parser.language` to populate the `parser_config` block. If these attributes are enum members, coerce them to their underlying string values (e.g., `getattr(parser.result_type, 'value', parser.result_type)`).
6. Scan the input directory non-recursively with `os.listdir` (or `pathlib.Path.iterdir`), filter to the allowed extensions, compute the per-file fields, and sort by `file_name`.
7. Write the JSON with `json.dump(..., indent=2)` so it is human-readable.
8. Print the success line and exit `0`. For the missing-directory error, print to `sys.stderr` and `sys.exit(1)`.

## Acceptance Criteria
- Project path: /home/user/parse_planner
- Script path: /home/user/parse_planner/parse_plan.py
- Command (happy path): `python3 /home/user/parse_planner/parse_plan.py --input-dir /home/user/parse_planner/inputs --output /home/user/parse_planner/plan.json --result-type markdown --num-workers 3 --language en`
  - Exit code: `0`.
  - Stdout (exact line): `Parse plan created with 2 files at /home/user/parse_planner/plan.json`
  - The file `/home/user/parse_planner/plan.json` exists and is valid JSON with the schema described above.
  - `parser_config` equals `{"result_type": "markdown", "num_workers": 3, "language": "en"}`.
  - `files` has exactly 2 entries, sorted by `file_name`, covering `data.txt` and `notes.md`. The unsupported `image.jpg` MUST be omitted.
  - Each file entry has the correct `path`, on-disk `size_bytes`, lowercase hex `sha256`, and `extra_info` equal to `{"file_name": <basename>}`.
- Command (error path): `python3 /home/user/parse_planner/parse_plan.py --input-dir /home/user/parse_planner/does_not_exist --output /home/user/parse_planner/should_not_exist.json`
  - Exit code: non-zero.
  - Stderr contains the line: `Error: input directory not found: /home/user/parse_planner/does_not_exist`
  - The file `/home/user/parse_planner/should_not_exist.json` must NOT be created.
- SDK usage: the script source must import `LlamaParse` from `llama_cloud_services` and must instantiate `LlamaParse(...)` (string match for both `from llama_cloud_services import LlamaParse` and `LlamaParse(`).

