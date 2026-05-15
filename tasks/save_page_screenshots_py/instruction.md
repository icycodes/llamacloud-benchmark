# Save LlamaParse Page Screenshots to Disk (Python)

## Background
LlamaCloud's v2 parsing service can render a high-resolution screenshot of every page of a document alongside the parsed text. In multimodal RAG pipelines this is useful when you want to keep a visual copy of every page (e.g. to feed it into a vision LLM later). When the parser is configured with `output_options.images_to_save = ["screenshot"]` the API exposes each page screenshot through a presigned download URL on the `images_content_metadata` field of the parse result. Your job is to build a small Python program that drives this end to end: upload a deterministic three-page PDF, parse it with screenshots enabled, download every per-page screenshot, and save each one as a PNG file on disk.

The task workspace `/home/user/screenshot_task` is pre-seeded with a three-page PDF at `/home/user/screenshot_task/sample.pdf`. The PDF is generated at image build time and is identical across runs. Each page contains a single, distinct marker phrase so the verifier can confirm the right document was parsed:
- Page 1: `Screenshot-Mode-Page-One`
- Page 2: `Screenshot-Mode-Page-Two`
- Page 3: `Screenshot-Mode-Page-Three`

## Requirements
- Read the current `trial_id` from `/logs/artifacts/trial_id`.
- Write a Python script `save_screenshots.py` in `/home/user/screenshot_task` that:
  - Authenticates against LlamaCloud using the `LLAMA_CLOUD_API_KEY` environment variable (the LlamaCloud SDK reads it automatically from the environment).
  - Uses the official LlamaCloud Python SDK (`llama-cloud` package, i.e. `from llama_cloud import LlamaCloud` or `from llama_cloud import AsyncLlamaCloud`) to upload `sample.pdf` with `purpose="parse"` and run a parse job.
  - Configures the parse job to use the `agentic` tier, asks the parser to render per-page screenshots via `output_options.images_to_save=["screenshot"]`, and requests both `markdown` (so the agent can produce the markdown output the parser tier requires) and `images_content_metadata` (so the script gets the presigned download URLs for the screenshots) on the result.
  - Iterates over the entries in `result.images_content_metadata.images`, downloads each presigned URL with an HTTP `GET`, and writes the bytes to a file under `/home/user/screenshot_task/screenshots/`. Each saved file must:
    - Be named `page_<NN>.png` where `<NN>` is the 1-indexed page number zero-padded to two digits (`page_01.png`, `page_02.png`, `page_03.png`).
    - Contain the raw PNG bytes returned by the presigned URL (the file must start with the standard PNG signature `\x89PNG\r\n\x1a\n` and be a valid image).
  - Writes a companion log file `/home/user/screenshot_task/output.log` whose contents are described in the Acceptance Criteria.
- The script must run end-to-end with `python3 save_screenshots.py` from `/home/user/screenshot_task` and exit with status code `0`.

## Implementation Hints
- The LlamaCloud Python SDK is already installed. `LlamaCloud()` instantiated with no arguments will pick up `LLAMA_CLOUD_API_KEY` from the environment automatically.
- Upload the PDF with `client.files.create(file="./sample.pdf", purpose="parse")` to obtain a file id, then call `client.parsing.parse(file_id=..., tier="agentic", version="latest", output_options={"images_to_save": ["screenshot"]}, expand=["markdown", "images_content_metadata"])`. The SDK polls the parse job to completion for you.
- The parse result exposes `result.images_content_metadata`, an object with an `images` list. Each entry has at least `.filename`, `.content_type` (e.g. `image/png`), and `.presigned_url`. Some entries also expose `.page_number` (1-indexed), but if not, you can infer the page order from the `.filename` or from the order of items in the list.
- Use the standard library (`urllib.request.urlopen(url).read()` is enough) or `requests.get(url).content` to download each presigned URL and write the bytes to disk. Make sure to create the output directory before writing.
- Read `trial_id` once at the top of the script and embed it in the log file so the verifier can correlate the run with the trial.

## Acceptance Criteria
- Project path: `/home/user/screenshot_task`
- Source PDF: `/home/user/screenshot_task/sample.pdf`
- Script path: `/home/user/screenshot_task/save_screenshots.py`
- Screenshot output directory: `/home/user/screenshot_task/screenshots/`
- Log file: `/home/user/screenshot_task/output.log`
- Command: `python3 /home/user/screenshot_task/save_screenshots.py` (run from `/home/user/screenshot_task`).
  - The command must exit with status code `0`.
- LlamaCloud usage:
  - `save_screenshots.py` must import from the `llama_cloud` Python SDK (the source must contain the literal substring `from llama_cloud` or `import llama_cloud`).
  - The source must contain the literal substring `images_to_save` so the executor wired the screenshot output option.
  - The source must contain the literal substring `images_content_metadata` so the executor opted into the presigned-URL response.
- The screenshot output directory must contain exactly three files: `page_01.png`, `page_02.png`, `page_03.png`. Each file must:
  - Have a non-zero size (at least 1024 bytes).
  - Start with the canonical PNG signature `\x89PNG\r\n\x1a\n` so the verifier can confirm the bytes are a real PNG.
- The log file `/home/user/screenshot_task/output.log` must contain:
  - A line of the form `Trial id: <trial_id>` where `<trial_id>` is the value read from `/logs/artifacts/trial_id`.
  - A line of the form `Parse job id: <job_id>` where `<job_id>` is the id of the parsing job returned by LlamaCloud.
  - A line of the form `Screenshot count: 3`.
  - A line of the form `Saved: page_01.png`.
  - A line of the form `Saved: page_02.png`.
  - A line of the form `Saved: page_03.png`.

