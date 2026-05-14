import os
import re
import pytest

PROJECT_DIR = "/home/user/catalog_task"
SCRIPT_PATH = os.path.join(PROJECT_DIR, "parse_selected.py")
OUTPUT_MD = os.path.join(PROJECT_DIR, "selected_pages.md")


def _read_script():
    with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
        return f.read()


def _read_output():
    with open(OUTPUT_MD, "r", encoding="utf-8") as f:
        return f.read()


def test_parse_script_exists():
    assert os.path.isfile(SCRIPT_PATH), (
        f"Expected the user's parsing script at {SCRIPT_PATH}, but it was not found."
    )


def test_parse_script_uses_llama_cloud_sdk():
    content = _read_script()
    assert "llama_cloud" in content, (
        f"{SCRIPT_PATH} must import from the llama_cloud SDK."
    )
    assert "LlamaCloud" in content, (
        f"{SCRIPT_PATH} must reference the LlamaCloud client class from the llama_cloud SDK."
    )
    assert "parsing.parse" in content, (
        f"{SCRIPT_PATH} must invoke client.parsing.parse(...) to start a LlamaParse job."
    )


def test_parse_script_passes_target_pages():
    content = _read_script()
    assert "page_ranges" in content, (
        f"{SCRIPT_PATH} must pass a `page_ranges` argument to client.parsing.parse(...)."
    )
    assert "target_pages" in content, (
        f"{SCRIPT_PATH} must specify `target_pages` inside `page_ranges`."
    )
    # Allow either single- or double-quoted "1,3" with optional whitespace, but it must be a string.
    pattern = re.compile(r"""target_pages\s*[:=]\s*['"]\s*1\s*,\s*3\s*['"]""")
    assert pattern.search(content) is not None, (
        f"{SCRIPT_PATH} must set target_pages to the string '1,3' (e.g. "
        f"page_ranges={{'target_pages': '1,3'}})."
    )


def test_parse_script_does_not_hardcode_api_key():
    content = _read_script()
    assert "llx-" not in content, (
        f"{SCRIPT_PATH} appears to hardcode a LlamaCloud API key (found 'llx-' prefix). "
        "The script must rely on the LLAMA_CLOUD_API_KEY environment variable."
    )


def test_output_md_exists():
    assert os.path.isfile(OUTPUT_MD), (
        f"Expected the parsed markdown output at {OUTPUT_MD}, but it was not found."
    )


def test_output_md_is_nonempty():
    assert os.path.getsize(OUTPUT_MD) > 0, (
        f"Output file {OUTPUT_MD} exists but is empty. LlamaParse should produce non-empty markdown."
    )


def test_output_md_contains_page1_product():
    content = _read_output().lower()
    assert "widget" in content, (
        f"Output markdown at {OUTPUT_MD} must contain 'Widget' (the product on page 1). "
        f"Got first 500 chars: {content[:500]!r}"
    )


def test_output_md_contains_page3_product():
    content = _read_output().lower()
    assert "sprocket" in content, (
        f"Output markdown at {OUTPUT_MD} must contain 'Sprocket' (the product on page 3). "
        f"Got first 500 chars: {content[:500]!r}"
    )


def test_output_md_excludes_page2_product():
    content = _read_output().lower()
    assert "bracket" not in content, (
        f"Output markdown at {OUTPUT_MD} must NOT contain 'Bracket' (page 2 was not targeted). "
        f"Got first 500 chars: {content[:500]!r}"
    )


def test_output_md_excludes_page4_product():
    content = _read_output().lower()
    assert "dynamo" not in content, (
        f"Output markdown at {OUTPUT_MD} must NOT contain 'Dynamo' (page 4 was not targeted). "
        f"Got first 500 chars: {content[:500]!r}"
    )
