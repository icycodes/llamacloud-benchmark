# Classify a Document with LlamaClassify (Python)

## Background
You are working in `/home/user/myproject`, which already contains a small text file named `document.txt` describing a business document. Your job is to build a Python command-line utility that uses the [LlamaCloud Python SDK](https://developers.llamaindex.ai/llamaparse/classify/sdk/) (the `llama-cloud` package, version 1.6 or newer) and the managed **LlamaClassify** service to classify the document into one of two pre-defined categories: `invoice` or `receipt`.

The SDK is already installed in the environment and the `LLAMA_CLOUD_API_KEY` environment variable is configured. You do NOT need to handle authentication explicitly — the SDK reads the API key from the environment automatically.

The convenience method `client.classifier.classify(...)` uploads, classifies, and waits for completion in a single call. Results are returned as a list of items; each item exposes a `result` attribute with `type`, `confidence`, and `reasoning` fields.

## Requirements
- Implement a Python CLI named `classify.py` at `/home/user/myproject/classify.py`.
- The script must accept exactly two command-line arguments:
  - `--input <path>`: the path to the local input file (typically `document.txt`).
  - `--output <path>`: the path where the classification result should be written as JSON.
- The script must use the **`llama-cloud`** Python SDK (`from llama_cloud import LlamaCloud`).
- Upload the input file with `purpose="classify"`.
- Submit a classification job using `client.classifier.classify(...)` with the following two rules (in this exact order):
  1. `type="invoice"`, `description="Documents that contain an invoice number, invoice date, bill-to section, and line items with totals."`
  2. `type="receipt"`, `description="Short purchase receipts, typically from POS systems, with merchant, items and total, often a single page."`
- Pass `mode="FAST"` to the classify call.
- After the call returns, take the first item from `result.items`. If `item.result` is `None`, exit with a non-zero status code.
- Otherwise, write a JSON object to the `--output` path (UTF-8, with `indent=2`) containing exactly these fields:
  - `type`: the classified type (string).
  - `confidence`: the confidence value as returned by the SDK.
  - `reasoning`: the reasoning string returned by the SDK.
- After a successful run, print a single line to stdout in the exact format: `Classified as: <type>` where `<type>` is the classified type from the result item.
- The script must exit with status code `0` on success and a non-zero status code if classification failed (no result available) or if the input file does not exist.

## Implementation Guide
1. Initialize the project at `/home/user/myproject`.
2. Parse `--input` and `--output` using `argparse` (standard library).
3. Instantiate `LlamaCloud()` — it reads `LLAMA_CLOUD_API_KEY` from the environment.
4. Upload the input file using `client.files.create(file=<input_path>, purpose="classify")` and capture the returned file id.
5. Call `client.classifier.classify(file_ids=[<file_id>], rules=[...], mode="FAST")` with the two rules described above.
6. Inspect `result.items[0]`. If `item.result` is `None`, exit non-zero.
7. Otherwise, build a dict with `type`, `confidence`, and `reasoning` and write it as pretty-printed JSON to `--output`.
8. Print `Classified as: <type>`.
9. Return exit code 0.

## Acceptance Criteria
- Project path: /home/user/myproject
- Script path: /home/user/myproject/classify.py
- Command: `python3 classify.py --input <input_path> --output <output_json_path>`
- Input argument format: `--input <path_to_input_file>` and `--output <path_to_output_json_file>`
- Expected stdout: includes exactly one line `Classified as: invoice` when the provided `document.txt` describes an invoice.
- The output JSON file must be created at the path specified by `--output` and must contain the fields `type`, `confidence`, and `reasoning`.
- The script must use the `llama-cloud` Python SDK with `mode="FAST"`.
- The classify call must include both rules (`type="invoice"` and `type="receipt"`) with the descriptions specified above.
- The script must succeed (exit code 0) when given a valid input file and a valid `LLAMA_CLOUD_API_KEY`.
- The script must exit with a non-zero status code when the input file does not exist.

