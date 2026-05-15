# Parse a Receipt PDF with a LlamaParse Custom Prompt (Python)

## Background
LlamaParse, LlamaCloud's agentic parser, supports a `custom_prompt` that lets you instruct the parsing agent in natural language. This is useful when the document contains a lot of noise (promotional text, survey codes, marketing) and you only care about a specific subset of the content (e.g. line items on a receipt). In this task you must build a small Python program that uses the official `llama-cloud` Python SDK to parse a deterministic receipt PDF with a custom prompt so that the markdown output contains **only** the receipt line items and the final amount due.

The task workspace `/home/user/prompted_parse_task` already contains the seeded receipt PDF at `/home/user/prompted_parse_task/sample.pdf`. The PDF is generated at image build time and is identical across runs. It includes:
- A merchant header block.
- A promotional / coupon section with a survey code that should be filtered out.
- A line-item table with three items (item name + price each):
  - `Big Mac Meal` — `$8.99`
  - `Snack Oreo McFlurry` — `$2.69`
  - `Happy Meal 6 Pc` — `$4.89`
- A totals block with a subtotal, tax, and the final `Total` of `$17.36`.

## Requirements
- Read the current `trial_id` from `/logs/artifacts/trial_id`.
- Write a Python script `parse_with_prompt.py` in `/home/user/prompted_parse_task` that:
  - Authenticates against LlamaCloud using the `LLAMA_CLOUD_API_KEY` environment variable (the LlamaCloud SDK reads it automatically from the environment).
  - Uses the official LlamaCloud Python SDK (`llama-cloud` package, i.e. `from llama_cloud import LlamaCloud` or `AsyncLlamaCloud`) to upload `sample.pdf` with `purpose="parse"` and run a parse job.
  - Passes a natural-language `custom_prompt` to the parser via `processing_options.auto_mode_configuration[].parsing_conf.custom_prompt`. The custom prompt must instruct the parser to keep only the line items (item name and price) and the final `Total` of the receipt, and to drop everything else (header, promotional text, survey codes, subtotal, tax).
  - Uses the `agentic` tier and asks for the markdown output via `expand=["markdown"]`.
  - Concatenates the markdown of every parsed page (separated by blank lines if there is more than one) and writes the full result to `/home/user/prompted_parse_task/output.md` as UTF-8 text.
  - Writes a companion log file `/home/user/prompted_parse_task/output.log` with the required fields described below so the verifier can correlate the produced artifacts with the trial.
- The script must run end-to-end with `python3 parse_with_prompt.py` from `/home/user/prompted_parse_task` and exit with status code `0`.

## Implementation Hints
- The LlamaCloud Python SDK is already installed. `LlamaCloud()` (or `AsyncLlamaCloud()`) instantiated with no arguments will pick up `LLAMA_CLOUD_API_KEY` from the environment automatically.
- Upload the PDF with `client.files.create(file="./sample.pdf", purpose="parse")` to obtain a file id, then call `client.parsing.parse(file_id=..., tier="agentic", version="latest", expand=["markdown"], processing_options=...)`. The SDK polls the job to completion for you.
- The `custom_prompt` lives on the `parsing_conf` of an `auto_mode_configuration` entry inside `processing_options`. The typed helpers `ProcessingOptions`, `ProcessingOptionsAutoModeConfiguration`, and `ProcessingOptionsAutoModeConfigurationParsingConf` are available in `llama_cloud.types.parsing_create_params`; plain dicts with the same shape also work.
- The result object exposes `.markdown.pages`, a list with one entry per page. Join the `.markdown` of every page to build the final markdown text.
- Read `trial_id` once at the top of the script and embed it in the log file so the verifier can correlate the run.
- Because the custom prompt is interpreted by an LLM the markdown shape may vary slightly between runs, but every required line item (item name + price) and the final total must remain in the output.

## Acceptance Criteria
- Project path: `/home/user/prompted_parse_task`
- Source PDF: `/home/user/prompted_parse_task/sample.pdf`
- Script path: `/home/user/prompted_parse_task/parse_with_prompt.py`
- Markdown output: `/home/user/prompted_parse_task/output.md`
- Log file: `/home/user/prompted_parse_task/output.log`
- Command: `python3 /home/user/prompted_parse_task/parse_with_prompt.py` (run from `/home/user/prompted_parse_task`).
  - The command must exit with status code `0`.
- LlamaCloud usage:
  - `parse_with_prompt.py` must import from the `llama_cloud` Python SDK (e.g. the literal substring `from llama_cloud` or `import llama_cloud`).
  - The parse job must be configured with a non-empty `custom_prompt` placed on a `parsing_conf` inside `processing_options.auto_mode_configuration` so the agentic parser receives the natural-language instruction.
- The markdown output `/home/user/prompted_parse_task/output.md` must:
  - Be a non-empty UTF-8 text file.
  - Contain every line-item name and its price from the seeded receipt (item names and the dollar prices).
  - Contain the final total of the receipt.
- The log file `/home/user/prompted_parse_task/output.log` must contain:
  - A line of the form `Trial id: <trial_id>` where `<trial_id>` is the value read from `/logs/artifacts/trial_id`.
  - A line of the form `Custom prompt: <prompt>` echoing the custom prompt string that was sent to the parser.
  - A line of the form `Parse job id: <job_id>` where `<job_id>` is the id of the parsing job returned by LlamaCloud.

