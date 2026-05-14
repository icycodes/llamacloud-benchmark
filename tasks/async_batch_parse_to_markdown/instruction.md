# Batch-Parse a Folder of PDFs Concurrently with `AsyncLlamaCloud`

## Background
LlamaCloud is LlamaIndex's managed RAG-as-a-Service platform. Its agentic document parser, LlamaParse, exposes both a synchronous `LlamaCloud` client and a fully asynchronous `AsyncLlamaCloud` client in the `llama_cloud` Python SDK. When you have a folder of documents to parse, the recommended high-throughput pattern is to drive parses concurrently via `AsyncLlamaCloud` plus `asyncio.gather`, optionally rate-limited with an `asyncio.Semaphore`, so that you are not waiting for each parse job to finish before starting the next.

In this task you must build that batch parsing pipeline for a small folder of pre-existing PDFs and emit a per-document markdown file.

## Requirements
Write a single Python script `batch_parse.py` (placed at `/home/user/batch_parse/batch_parse.py`) that:

1. Imports the **async** client: `from llama_cloud import AsyncLlamaCloud`.
2. Reads the API key from the `LLAMA_CLOUD_API_KEY` environment variable (do **not** hardcode it; either instantiate `AsyncLlamaCloud()` with no arguments — the SDK will pick the env var up — or pass `api_key=os.getenv("LLAMA_CLOUD_API_KEY")`).
3. Discovers every `*.pdf` file inside `/home/user/batch_parse/pdfs/` (there are three: `alpha.pdf`, `bravo.pdf`, `charlie.pdf`).
4. For every PDF concurrently:
   - Uploads it via `await client.files.create(file=<absolute path>, purpose="parse")`.
   - Submits an agentic parse job via `await client.parsing.parse(file_id=<uploaded.id>, tier="agentic", version="latest", expand=["markdown"])`.
   - Concatenates `result.markdown.pages[*].markdown` in page order (use a single newline between pages).
   - Writes the concatenated markdown to `/home/user/batch_parse/out/<basename>.md` (UTF-8) where `<basename>` is the PDF file name without the `.pdf` extension (e.g. `alpha.pdf` → `out/alpha.md`).
5. Drives the per-file coroutines concurrently using `asyncio.gather` (NOT a sequential `for ... await ...` loop) and wraps the work in an `async def main(): ...` coroutine launched with `asyncio.run(main())`.
6. Creates the output directory `/home/user/batch_parse/out/` if it does not already exist.

## Implementation Guide
1. `cd /home/user/batch_parse`.
2. Create `batch_parse.py` along these lines:
   ```python
   import asyncio
   import os
   from pathlib import Path

   from llama_cloud import AsyncLlamaCloud

   PDF_DIR = Path("/home/user/batch_parse/pdfs")
   OUT_DIR = Path("/home/user/batch_parse/out")


   async def parse_one(client: AsyncLlamaCloud, pdf_path: Path) -> None:
       uploaded = await client.files.create(file=str(pdf_path), purpose="parse")
       result = await client.parsing.parse(
           file_id=uploaded.id,
           tier="agentic",
           version="latest",
           expand=["markdown"],
       )
       parts = [(p.markdown or "") for p in result.markdown.pages]
       combined = "\n".join(parts)
       out_path = OUT_DIR / f"{pdf_path.stem}.md"
       out_path.write_text(combined, encoding="utf-8")


   async def main() -> None:
       OUT_DIR.mkdir(parents=True, exist_ok=True)
       client = AsyncLlamaCloud(api_key=os.environ["LLAMA_CLOUD_API_KEY"])
       pdf_paths = sorted(PDF_DIR.glob("*.pdf"))
       await asyncio.gather(*(parse_one(client, p) for p in pdf_paths))


   asyncio.run(main())
   ```
3. Run it with `python3 batch_parse.py` from `/home/user/batch_parse`. The script blocks until all three parse jobs finish concurrently.
4. Confirm that `/home/user/batch_parse/out/alpha.md`, `/home/user/batch_parse/out/bravo.md`, and `/home/user/batch_parse/out/charlie.md` were all written.

## Constraints
- Project path: `/home/user/batch_parse`
- Input directory: `/home/user/batch_parse/pdfs/` (already populated with `alpha.pdf`, `bravo.pdf`, `charlie.pdf`)
- Output directory: `/home/user/batch_parse/out/` (must be created by the script if missing)
- Script path: `/home/user/batch_parse/batch_parse.py`
- Output files (UTF-8):
  - `/home/user/batch_parse/out/alpha.md`
  - `/home/user/batch_parse/out/bravo.md`
  - `/home/user/batch_parse/out/charlie.md`
- Use the **async** client `AsyncLlamaCloud` from the `llama_cloud` SDK. Do NOT use the synchronous `LlamaCloud` client. Do NOT call the REST API directly with `curl`, `requests`, or `httpx`.
- Drive parses concurrently with `asyncio.gather`. A purely sequential `for ... await client.parsing.parse(...)` loop is NOT acceptable.
- The script must rely on `LLAMA_CLOUD_API_KEY` from the environment — no hardcoded `llx-...` literal anywhere in the script.
- Each output markdown file MUST contain the unique marker phrase from the corresponding source PDF (see Specific Test Data in the verification plan).

## Integrations
- LlamaCloud (LlamaParse) — requires the `LLAMA_CLOUD_API_KEY` environment variable.
