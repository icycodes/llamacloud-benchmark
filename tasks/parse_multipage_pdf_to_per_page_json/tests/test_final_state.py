import json
import os
import subprocess
import pytest

PROJECT_DIR = "/home/user/myproject"
PARSE_SCRIPT = os.path.join(PROJECT_DIR, "parse_pages.py")
PAGES_JSON = os.path.join(PROJECT_DIR, "pages.json")
REPORT_PDF = os.path.join(PROJECT_DIR, "report.pdf")


def _maybe_run_parse_script():
    """If the agent did not leave the output JSON in place, re-run the script
    once with the verifier's LLAMA_CLOUD_API_KEY so the artifact is present
    for the assertions below."""
    if os.path.isfile(PAGES_JSON):
        return
    if not os.path.isfile(PARSE_SCRIPT):
        return
    subprocess.run(
        ["python3", PARSE_SCRIPT],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=300,
    )


def _load_pages_json():
    _maybe_run_parse_script()
    assert os.path.isfile(PAGES_JSON), \
        f"Expected parsed per-page JSON at {PAGES_JSON}, but it does not exist."
    with open(PAGES_JSON, "r", encoding="utf-8", errors="replace") as f:
        return json.load(f)


def test_parse_script_exists():
    assert os.path.isfile(PARSE_SCRIPT), \
        f"Expected the agent to create {PARSE_SCRIPT}, but it does not exist."


def test_parse_script_uses_llamaparse_sdk():
    with open(PARSE_SCRIPT, "r", encoding="utf-8", errors="replace") as f:
        contents = f.read()
    uses_services = "llama_cloud_services" in contents or "llama-cloud-services" in contents
    uses_client = "llama_cloud" in contents or "LlamaCloud" in contents or "LlamaParse" in contents
    assert uses_services or uses_client, (
        "parse_pages.py must import or reference a LlamaParse client from either "
        "'llama_cloud_services' or 'llama_cloud'."
    )


def test_report_pdf_unchanged():
    assert os.path.isfile(REPORT_PDF), \
        f"Source PDF {REPORT_PDF} must remain in place."
    with open(REPORT_PDF, "rb") as f:
        header = f.read(5)
    assert header.startswith(b"%PDF-"), \
        f"Source PDF {REPORT_PDF} is no longer a valid PDF."


def test_pages_json_exists_and_non_empty():
    _maybe_run_parse_script()
    assert os.path.isfile(PAGES_JSON), \
        f"Expected parsed JSON at {PAGES_JSON}, but it does not exist."
    assert os.path.getsize(PAGES_JSON) > 0, \
        f"Parsed JSON file {PAGES_JSON} is empty."


def test_pages_json_top_level_structure():
    data = _load_pages_json()
    assert isinstance(data, dict), \
        f"Top-level JSON value must be an object, got: {type(data).__name__}"
    for key in ("source", "page_count", "pages"):
        assert key in data, f"Top-level JSON object is missing required key: {key!r}"
    assert isinstance(data["pages"], list), \
        f"'pages' must be a JSON list, got: {type(data['pages']).__name__}"


def test_pages_json_page_count_matches():
    data = _load_pages_json()
    assert isinstance(data["page_count"], int), \
        f"'page_count' must be an integer, got: {type(data['page_count']).__name__}"
    assert data["page_count"] == 3, \
        f"Expected page_count == 3 (the source PDF has 3 pages), got: {data['page_count']}"
    assert len(data["pages"]) == 3, \
        f"Expected exactly 3 entries in 'pages', got: {len(data['pages'])}"


def test_pages_have_correct_shape_and_ordering():
    data = _load_pages_json()
    pages = data["pages"]
    page_numbers = []
    for idx, entry in enumerate(pages):
        assert isinstance(entry, dict), \
            f"pages[{idx}] must be a JSON object, got: {type(entry).__name__}"
        assert "page" in entry and "markdown" in entry, \
            f"pages[{idx}] must contain 'page' and 'markdown' keys, got: {list(entry.keys())}"
        assert isinstance(entry["page"], int), \
            f"pages[{idx}]['page'] must be an integer, got: {type(entry['page']).__name__}"
        assert isinstance(entry["markdown"], str) and entry["markdown"].strip() != "", \
            f"pages[{idx}]['markdown'] must be a non-empty string."
        page_numbers.append(entry["page"])
    assert page_numbers == [1, 2, 3], \
        f"Expected page numbers [1, 2, 3] in ascending order, got: {page_numbers}"


def test_page_1_contains_expected_content():
    data = _load_pages_json()
    page1 = data["pages"][0]["markdown"]
    assert "Acme Corporation" in page1, (
        f"Expected page 1 markdown to contain 'Acme Corporation', "
        f"got first 500 chars:\n{page1[:500]}"
    )
    assert "Annual Report 2024" in page1, (
        f"Expected page 1 markdown to contain 'Annual Report 2024', "
        f"got first 500 chars:\n{page1[:500]}"
    )


def test_page_2_contains_expected_content():
    data = _load_pages_json()
    page2 = data["pages"][1]["markdown"]
    assert "Quarterly Breakdown" in page2, (
        f"Expected page 2 markdown to contain 'Quarterly Breakdown', "
        f"got first 500 chars:\n{page2[:500]}"
    )
    assert "Q3" in page2, (
        f"Expected page 2 markdown to contain 'Q3', "
        f"got first 500 chars:\n{page2[:500]}"
    )


def test_page_3_contains_expected_content():
    data = _load_pages_json()
    page3 = data["pages"][2]["markdown"]
    assert "Outlook" in page3, (
        f"Expected page 3 markdown to contain 'Outlook', "
        f"got first 500 chars:\n{page3[:500]}"
    )
    assert "2025" in page3, (
        f"Expected page 3 markdown to contain '2025', "
        f"got first 500 chars:\n{page3[:500]}"
    )
