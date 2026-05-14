# Preserve Hyperlink Destinations When Parsing a PDF with LlamaParse (`annotate_links`)

## Background
LlamaCloud is LlamaIndex's managed RAG-as-a-Service platform. Its agentic document parser, LlamaParse, converts visually rich PDFs into clean markdown. By default LlamaParse renders link **anchor text** in the markdown output, but the underlying URLs are dropped — which is unhelpful for downstream RAG pipelines that want to retain citations and follow-up references.

Flipping `output_options.markdown.annotate_links` to `True` instructs LlamaParse to preserve link destinations in the rendered markdown (so a hyperlink that says "Visit our docs" pointing at `https://example.com/docs` is rendered as a markdown link such as `[Visit our docs](https://example.com/docs)` instead of plain text).

In this task you must build a small pipeline that parses a single-page PDF containing two embedded hyperlinks and writes the link-annotated markdown to disk so the URLs are retained.

## Requirements
Write a Python script `parse_with_links.py` that uses the `llama-cloud` SDK (`from llama_cloud import LlamaCloud`) to:
  1. Upload the local PDF `references.pdf` to LlamaCloud with `purpose="parse"`.
  2. Submit a parse job with all of the following options:
     - `tier="agentic"`
     - `version="latest"`
     - `output_options={"markdown": {"annotate_links": True}}` (so the URL of every hyperlink in the PDF is preserved in the rendered markdown)
     - `expand=["markdown"]`
  3. Concatenate the `markdown` field of every page returned by the parser (`result.markdown.pages`) in order, using a single newline as the separator between pages.
  4. Write that concatenated markdown to `links_output.md` in the same directory (UTF-8 encoded).

The script must authenticate via the `LLAMA_CLOUD_API_KEY` environment variable (the SDK reads it automatically when `LlamaCloud()` is instantiated with no arguments). Do NOT hardcode an API key.

## Implementation Guide
1. Change into the project directory `/home/user/links_task`.
2. Create `parse_with_links.py` with logic similar to:
   ```python
   from llama_cloud import LlamaCloud

   client = LlamaCloud()  # reads LLAMA_CLOUD_API_KEY from the environment
   uploaded = client.files.create(file="./references.pdf", purpose="parse")
   result = client.parsing.parse(
       file_id=uploaded.id,
       tier="agentic",
       version="latest",
       output_options={
           "markdown": {"annotate_links": True},
       },
       expand=["markdown"],
   )

   parts = [(p.markdown or "") for p in result.markdown.pages]
   combined = "\n".join(parts)
   with open("links_output.md", "w", encoding="utf-8") as f:
       f.write(combined)
   ```
3. Execute the script with `python3 parse_with_links.py` from `/home/user/links_task`. The script will block until LlamaCloud finishes parsing and then writes the markdown file.
4. Confirm that `links_output.md` has been written.

## Constraints
- Project path: `/home/user/links_task`
- Input file: `/home/user/links_task/references.pdf` (already provided — a 1-page PDF with two embedded hyperlinks)
- Output file: `/home/user/links_task/links_output.md`
- Script path: `/home/user/links_task/parse_with_links.py`
- Use the `llama-cloud` SDK (the `LlamaCloud` client class). Do NOT call the REST API directly with `curl` or `requests`.
- The parse call MUST pass `output_options` with `markdown.annotate_links` set to `True`. This is the documented switch that preserves link destinations in the rendered markdown.
- The script must rely on `LLAMA_CLOUD_API_KEY` from the environment, not hardcoded.
- The resulting `links_output.md` must preserve both source URLs verbatim: `https://example.com/docs` and `https://llamaindex.ai`.

## Integrations
- LlamaCloud (LlamaParse) — requires the `LLAMA_CLOUD_API_KEY` environment variable.
