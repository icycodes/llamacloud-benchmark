# Download Per-Page Screenshots from a LlamaParse Job

## Background
LlamaCloud is LlamaIndex's managed RAG-as-a-Service platform. Its agentic document parser, LlamaParse, can render every page of a parsed document as a PNG screenshot — this is a common building block for multimodal RAG pipelines that want to feed both extracted text and the page image into a VLM. The pattern is two-stage:

1. **Generate** the screenshots at parse time by setting `output_options={"images_to_save": ["screenshot"]}`.
2. **Fetch** them via the `images_content_metadata` expand value, which returns a structured list of `{ filename, presigned_url, ... }` entries. You then download each `presigned_url` with a normal HTTP GET and save the bytes to disk.

A common mistake here is to omit `images_to_save` (in which case the screenshots are never generated and `images_content_metadata.images` comes back empty), or to forget that `images_content_metadata` does NOT inline the bytes — you have to fetch each `presigned_url` yourself.

In this task you must implement that two-stage pipeline end-to-end against a pre-existing 3-page PDF.

## Pre-existing Layout
The project directory `/home/user/screenshot_task` already contains:

```
/home/user/screenshot_task/
└── report.pdf            # 3-page PDF, generated deterministically at image-build time
```

The 3 pages contain the section titles `Alpha Section`, `Bravo Section`, and `Charlie Section` respectively, in that order.

## Requirements

Create a single Python script `download_screenshots.py` at `/home/user/screenshot_task/download_screenshots.py` that:

1. Imports the synchronous client: `from llama_cloud import LlamaCloud`.
2. Authenticates using the `LLAMA_CLOUD_API_KEY` environment variable. Instantiate `LlamaCloud()` with no arguments (the SDK reads the key from the environment) or pass `token=os.environ["LLAMA_CLOUD_API_KEY"]`. **Do NOT hardcode the API key in the script** (no `llx-...` literal).
3. Uploads `/home/user/screenshot_task/report.pdf` to LlamaCloud via:
   ```python
   uploaded = client.files.create(file="/home/user/screenshot_task/report.pdf", purpose="parse")
   ```
4. Invokes `client.parsing.parse(...)` EXACTLY ONCE with:
   - `file_id=uploaded.id`
   - `tier="agentic"`
   - `version="latest"`
   - `output_options={"images_to_save": ["screenshot"]}` (this is what causes screenshots to be generated)
   - `expand=["images_content_metadata"]` (so the response contains the list of presigned image URLs)
5. Reads the resulting `result.images_content_metadata.images` list (each entry has `filename`, `presigned_url`, `content_type`, `size_bytes`, and `index`).
6. For every image entry, downloads the bytes from `presigned_url` and writes them to `/home/user/screenshot_task/screenshots/<filename>` (the bytes MUST be the raw response body — do NOT re-encode). Use `urllib.request` from the standard library, or `requests`/`httpx` if you prefer (you may install nothing extra; `urllib.request` is preinstalled). Create the `screenshots/` directory if it does not already exist.
7. After all downloads succeed, writes a manifest file `/home/user/screenshot_task/manifest.json` (UTF-8, `indent=2`) with this exact shape:
   ```json
   {
     "source": "report.pdf",
     "job_id": "<the parse job id>",
     "page_count": 3,
     "image_count": <int, must equal len(images)>,
     "images": [
       { "filename": "<filename>", "size_bytes": <int>, "saved_path": "/home/user/screenshot_task/screenshots/<filename>" },
       ...
     ]
   }
   ```
   Rules for the manifest:
   - `source` MUST be the literal string `"report.pdf"`.
   - `job_id` MUST be the parse job's id (`result.job.id`).
   - `page_count` MUST be the integer `3`.
   - `image_count` MUST equal `len(result.images_content_metadata.images)` and MUST equal the number of files written under `screenshots/`.
   - `images` MUST be a list, one entry per saved file, ordered by ascending `index` from the LlamaParse response.
   - Each entry's `size_bytes` MUST equal the actual on-disk size of the saved file in bytes.
   - Each entry's `saved_path` MUST be the absolute path of the saved file (`/home/user/screenshot_task/screenshots/<filename>`).
8. The script must run end-to-end as `python3 download_screenshots.py` from `/home/user/screenshot_task` and exit with status 0.

## Implementation Guide

1. `cd /home/user/screenshot_task`.
2. Create `download_screenshots.py`. A reference implementation:
   ```python
   import json
   import os
   import urllib.request
   from pathlib import Path

   from llama_cloud import LlamaCloud

   PROJECT_DIR = Path("/home/user/screenshot_task")
   PDF_PATH = PROJECT_DIR / "report.pdf"
   SCREENSHOTS_DIR = PROJECT_DIR / "screenshots"
   MANIFEST_PATH = PROJECT_DIR / "manifest.json"


   def main() -> None:
       SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

       client = LlamaCloud()  # reads LLAMA_CLOUD_API_KEY from the environment

       uploaded = client.files.create(file=str(PDF_PATH), purpose="parse")

       result = client.parsing.parse(
           file_id=uploaded.id,
           tier="agentic",
           version="latest",
           output_options={"images_to_save": ["screenshot"]},
           expand=["images_content_metadata"],
       )

       images = sorted(
           list(result.images_content_metadata.images),
           key=lambda im: im.index,
       )

       manifest_entries = []
       for image in images:
           dst = SCREENSHOTS_DIR / image.filename
           with urllib.request.urlopen(image.presigned_url) as resp:
               data = resp.read()
           dst.write_bytes(data)
           manifest_entries.append({
               "filename": image.filename,
               "size_bytes": dst.stat().st_size,
               "saved_path": str(dst),
           })

       manifest = {
           "source": "report.pdf",
           "job_id": result.job.id,
           "page_count": 3,
           "image_count": len(manifest_entries),
           "images": manifest_entries,
       }
       with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
           json.dump(manifest, f, indent=2)


   main()
   ```
3. Run the script:
   ```bash
   cd /home/user/screenshot_task
   python3 download_screenshots.py
   ```
4. Confirm the artifacts exist:
   - `/home/user/screenshot_task/screenshots/` contains one image file per page.
   - `/home/user/screenshot_task/manifest.json` lists every saved image.

## Constraints
- Project path: `/home/user/screenshot_task`
- Input PDF: `/home/user/screenshot_task/report.pdf` (must not be modified)
- Script path: `/home/user/screenshot_task/download_screenshots.py`
- Screenshots directory: `/home/user/screenshot_task/screenshots/`
- Manifest file: `/home/user/screenshot_task/manifest.json`
- Use the official `llama_cloud` Python SDK (`from llama_cloud import LlamaCloud`). Do NOT call the LlamaCloud REST API directly with `curl`, `requests`, or `httpx`; the only HTTP traffic outside the SDK is the S3 presigned URL download.
- The script must rely on `LLAMA_CLOUD_API_KEY` from the environment — no hardcoded `llx-...` literal anywhere.
- `client.parsing.parse(...)` MUST be invoked exactly once. Do NOT issue a second `parsing.parse(...)` call (e.g. once without `images_to_save` and once with) — the screenshots MUST be requested in the single parse call.
- The `output_options` argument passed to `parsing.parse` MUST include `"images_to_save"` containing the literal string `"screenshot"`. The `expand` argument MUST include the literal string `"images_content_metadata"`.
- The image files saved to disk MUST be the raw bytes returned by the presigned URLs (do NOT re-encode them or wrap them in JSON).
- The PDF has 3 pages, so the manifest's `page_count` MUST be `3` and `image_count` MUST be `>= 1`.

## Integrations
- LlamaCloud (LlamaParse) — requires the `LLAMA_CLOUD_API_KEY` environment variable. The presigned URL download targets `s3.amazonaws.com` (or a comparable LlamaCloud-managed bucket) and requires outbound internet access.
