When processing file uploads directly from web requests in memory, developers pass raw bytes to the parser. However, LlamaParse relies on file extensions to determine parsing strategies, causing the API to fail if metadata is missing.

You need to write a Python function `parse_pdf_bytes(pdf_bytes: bytes) -> str` in `parse_bytes.py` that utilizes `LlamaParse` to parse raw document bytes. To bypass the API failure, you must provide the correct metadata dictionary to the parsing method (e.g., using `extra_info={"file_name": "document.pdf"}`). The function should return the parsed markdown text.

**Constraints:**
- The function must directly accept and process raw `bytes` in memory, not a file path.
- The `result_type` for `LlamaParse` must be set to "markdown".
- You must explicitly define `extra_info` with a mock file name to prevent the API 400 error.