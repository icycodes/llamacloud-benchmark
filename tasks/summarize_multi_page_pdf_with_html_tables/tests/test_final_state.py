import json
import os
import re
import pytest

PROJECT_DIR = "/home/user/ops_report"
SCRIPT_PATH = os.path.join(PROJECT_DIR, "summarize_report.py")
SUMMARY_JSON = os.path.join(PROJECT_DIR, "summary.json")


def _load_summary():
    with open(SUMMARY_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def test_summarize_script_exists():
    assert os.path.isfile(SCRIPT_PATH), (
        f"Expected the user's summarization script at {SCRIPT_PATH}, but it was not found."
    )


def test_summarize_script_uses_llama_cloud_sdk():
    with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    assert "LlamaCloud" in content, (
        f"{SCRIPT_PATH} must reference the LlamaCloud client class from the llama_cloud SDK."
    )
    assert "llama_cloud" in content, (
        f"{SCRIPT_PATH} must import from the llama_cloud SDK."
    )
    assert "parsing.parse" in content, (
        f"{SCRIPT_PATH} must invoke client.parsing.parse(...) to start a LlamaParse job."
    )


def test_summarize_script_configures_html_tables_output():
    with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    assert "output_options" in content, (
        f"{SCRIPT_PATH} must pass output_options to client.parsing.parse(...) so tables come back as HTML."
    )
    # output_tables_as_markdown must be set to False (Python literal). Match the
    # key and the False value with arbitrary whitespace between them.
    pattern = re.compile(r"output_tables_as_markdown\s*[:=]\s*False")
    assert pattern.search(content), (
        f"{SCRIPT_PATH} must set output_options.markdown.tables.output_tables_as_markdown to False "
        f"so that LlamaParse emits HTML <table> blocks instead of pipe-table markdown."
    )


def test_summarize_script_does_not_hardcode_api_key():
    with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    assert "llx-" not in content, (
        f"{SCRIPT_PATH} appears to hardcode a LlamaCloud API key (found 'llx-' prefix). "
        "The script must rely on the LLAMA_CLOUD_API_KEY environment variable."
    )


def test_summary_json_exists_and_nonempty():
    assert os.path.isfile(SUMMARY_JSON), (
        f"Expected the summary JSON at {SUMMARY_JSON}, but it was not found."
    )
    assert os.path.getsize(SUMMARY_JSON) > 0, (
        f"Summary JSON file {SUMMARY_JSON} exists but is empty."
    )


def test_summary_json_is_valid_json_with_expected_top_level_keys():
    data = _load_summary()
    assert isinstance(data, dict), (
        f"summary.json must be a JSON object at the top level, got {type(data).__name__}."
    )
    expected_keys = {"total_pages", "pages", "html_tables"}
    assert set(data.keys()) == expected_keys, (
        f"summary.json must have exactly the top-level keys {sorted(expected_keys)}, "
        f"got {sorted(data.keys())}."
    )


def test_summary_total_pages_is_three():
    data = _load_summary()
    assert data["total_pages"] == 3, (
        f"Expected total_pages == 3 in summary.json, got {data['total_pages']!r}."
    )
    assert isinstance(data["total_pages"], int) and not isinstance(
        data["total_pages"], bool
    ), (
        f"Expected total_pages to be an int (not bool/str), got type "
        f"{type(data['total_pages']).__name__}."
    )


def test_summary_pages_structure():
    data = _load_summary()
    pages = data["pages"]
    assert isinstance(pages, list), (
        f"Expected 'pages' to be a list, got {type(pages).__name__}."
    )
    assert len(pages) == 3, (
        f"Expected 'pages' to contain exactly 3 entries, got {len(pages)}."
    )
    for idx, page in enumerate(pages, start=1):
        assert isinstance(page, dict), (
            f"pages[{idx - 1}] must be an object, got {type(page).__name__}."
        )
        assert set(page.keys()) == {"page_number", "word_count", "has_html_table"}, (
            f"pages[{idx - 1}] must have exactly the keys "
            f"['has_html_table', 'page_number', 'word_count'], got {sorted(page.keys())}."
        )
        assert page["page_number"] == idx, (
            f"pages[{idx - 1}].page_number must be {idx}, got {page['page_number']!r}."
        )
        assert isinstance(page["word_count"], int) and not isinstance(
            page["word_count"], bool
        ), (
            f"pages[{idx - 1}].word_count must be an int, got type "
            f"{type(page['word_count']).__name__}."
        )
        assert page["word_count"] > 0, (
            f"pages[{idx - 1}].word_count must be a positive integer, got {page['word_count']}."
        )
        assert isinstance(page["has_html_table"], bool), (
            f"pages[{idx - 1}].has_html_table must be a bool (not str/int), got type "
            f"{type(page['has_html_table']).__name__}."
        )


def test_summary_has_html_table_flags_match_source_pdf():
    data = _load_summary()
    flags = [p["has_html_table"] for p in data["pages"]]
    assert flags == [False, True, True], (
        f"Expected has_html_table flags [False, True, True] (page 1 has no table; "
        f"pages 2 and 3 contain tables), got {flags!r}."
    )


def test_summary_html_tables_list():
    data = _load_summary()
    html_tables = data["html_tables"]
    assert isinstance(html_tables, list), (
        f"Expected 'html_tables' to be a list, got {type(html_tables).__name__}."
    )
    assert len(html_tables) == 2, (
        f"Expected 'html_tables' to contain exactly 2 entries (one per page that has a table), "
        f"got {len(html_tables)}."
    )
    for i, entry in enumerate(html_tables):
        assert isinstance(entry, str), (
            f"html_tables[{i}] must be a string, got {type(entry).__name__}."
        )
        assert "<table" in entry.lower(), (
            f"html_tables[{i}] must contain an HTML opening table tag (substring '<table' "
            f"case-insensitive). First 200 chars: {entry[:200]!r}"
        )
