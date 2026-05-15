# Parse Only Specific Pages of a Multi-Page PDF with LlamaParse `target_pages` (Python)

## Background
LlamaCloud's LlamaParse parser supports a `target_pages` argument that lets you parse only a subset of the pages of a multi-page PDF, which is helpful for very large documents where you already know which pages are interesting and want to avoid paying for the rest. In this task you must build a small Python program that uses LlamaParse to extract markdown from **only pages 1 and 3** (zero-indexed) of a deterministic five-page PDF, and write the extracted markdown plus a small log file that the verifier will inspect.

The task workspace `/home/user/parse_pages_task` is pre-seeded with a five-page PDF at `/home/user/parse_pages_task/sample.pdf` (generated at image build time, identical across runs). Each page contains exactly one visible marker phrase so that the verifier can confirm which pages were actually parsed:

- Page index `0`: `Marker-Alpha-Page-Zero`
- Page index `1`: `Marker-Bravo-Page-One`
- Page index `2`: `Marker-Charlie-Page-Two`
- Page index `3`: `Marker-Delta-Page-Three`
- Page index `4`: `Marker-Echo-Page-Four`

## Requirements
- Read the current `trial_id` from `/logs/artifacts/trial_id`.
- Write a Python script `parse_pages.py` in `/home/user/parse_pages_task` that:
  - Authenticates against LlamaCloud using the `LLAMA_CLOUD_API_KEY` environment variable.
  - Uses the official LlamaParse Python SDK (e.g. `from llama_cloud_services import LlamaParse` or `from llama_parse import LlamaParse`) to parse `sample.pdf`.
  - Configures the parser with `result_type="markdown"` and `target_pages="1,3"` so that only the second and fourth pages of the PDF (0-indexed pages `1` and `3`) are parsed.
  - Concatenates the markdown returned for the parsed pages (separated by blank lines if there is more than one) and writes the full markdown to `/home/user/parse_pages_task/output.md` as UTF-8 text.
  - Writes a companion log file `/home/user/parse_pages_task/output.log` so the verifier can correlate the produced artifacts with the trial (see Acceptance Criteria for the exact lines that must appear).
- The script must run end-to-end with `python3 parse_pages.py` from `/home/user/parse_pages_task` and exit with status code `0`.

## Implementation Hints
- The LlamaParse Python SDK reads `LLAMA_CLOUD_API_KEY` automatically when the environment variable is set, so you don't have to pass `api_key=...` explicitly.
- `LlamaParse` accepts the `target_pages` argument as a comma-separated string of 0-indexed page numbers (range syntax such as `0-2,5` is also supported). To skip pages `0`, `2`, and `4` of this PDF, pass `target_pages="1,3"`.
- Call `parser.load_data("./sample.pdf")` to get back a list of `Document` objects whose `.text` attribute is the markdown for the parsed pages. Joining the `.text` of every returned document with `"\n\n"` is enough to assemble the final markdown.
- Read `trial_id` once at the top of the script and embed it in the log file so the verifier can correlate the run with the trial.

## Acceptance Criteria
- Project path: `/home/user/parse_pages_task`
- Source PDF: `/home/user/parse_pages_task/sample.pdf`
- Script path: `/home/user/parse_pages_task/parse_pages.py`
- Markdown output: `/home/user/parse_pages_task/output.md`
- Log file: `/home/user/parse_pages_task/output.log`
- Command: `python3 /home/user/parse_pages_task/parse_pages.py` (run from `/home/user/parse_pages_task`).
  - The command must exit with status code `0`.
- LlamaParse usage:
  - `parse_pages.py` must import LlamaParse from either `llama_cloud_services` or `llama_parse` (e.g. the literal substring `from llama_cloud_services import` or `from llama_parse import`).
  - The source file must contain the literal substring `target_pages` (proving the executor configured the feature).
- The markdown output `/home/user/parse_pages_task/output.md` must:
  - Be a non-empty UTF-8 text file.
  - Contain the marker phrases from the two pages that were requested (`Marker-Bravo-Page-One` and `Marker-Delta-Page-Three`).
  - **Not** contain the marker phrases from the three pages that were skipped (`Marker-Alpha-Page-Zero`, `Marker-Charlie-Page-Two`, and `Marker-Echo-Page-Four`).
- The log file `/home/user/parse_pages_task/output.log` must contain:
  - A line of the form `Trial id: <trial_id>` where `<trial_id>` is the value read from `/logs/artifacts/trial_id`.
  - A line of the form `Target pages: 1,3` echoing the exact `target_pages` string that was sent to the parser.
  - A line of the form `Parsed pages count: <N>` where `<N>` is the number of pages LlamaParse returned for this job; it must be exactly `2` because two pages were requested.

