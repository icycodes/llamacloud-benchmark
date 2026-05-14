import os
import re

PROJECT_DIR = "/home/user/links_task"
SCRIPT_PATH = os.path.join(PROJECT_DIR, "parse_with_links.py")
OUTPUT_MD = os.path.join(PROJECT_DIR, "links_output.md")


def _read_script():
    with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
        return f.read()


def _read_output_md():
    with open(OUTPUT_MD, "r", encoding="utf-8") as f:
        return f.read()


def test_parse_script_exists():
    assert os.path.isfile(SCRIPT_PATH), (
        f"Expected the user's parsing script at {SCRIPT_PATH}, but it was not found."
    )


def test_parse_script_uses_llama_cloud_sdk():
    content = _read_script()
    assert "llama_cloud" in content, (
        f"{SCRIPT_PATH} must import from the llama_cloud SDK (substring 'llama_cloud')."
    )
    assert "LlamaCloud" in content, (
        f"{SCRIPT_PATH} must reference the LlamaCloud client class from the llama_cloud SDK."
    )
    assert "parsing.parse" in content, (
        f"{SCRIPT_PATH} must invoke client.parsing.parse(...) to start a LlamaParse job."
    )


def test_parse_script_does_not_use_raw_http():
    """The task requires the SDK, not raw HTTP calls."""
    content = _read_script()
    forbidden_imports = (
        "import requests",
        "from requests",
        "import httpx",
        "from httpx",
        "subprocess.run([\"curl",
        "subprocess.run(['curl",
    )
    for needle in forbidden_imports:
        assert needle not in content, (
            f"{SCRIPT_PATH} must use the llama_cloud SDK, not raw HTTP (found '{needle}')."
        )


def test_parse_script_passes_annotate_links_true():
    """The script must pass output_options with markdown.annotate_links=True."""
    content = _read_script()
    assert "annotate_links" in content, (
        f"{SCRIPT_PATH} must pass output_options.markdown.annotate_links to the parse call "
        "to preserve link destinations."
    )
    # Allow either `annotate_links=True`, `annotate_links: True`, `'annotate_links': True`,
    # or `"annotate_links": True`, possibly with whitespace.
    pattern = re.compile(
        r"""['\"]?annotate_links['\"]?\s*[:=]\s*True""",
        re.MULTILINE,
    )
    assert pattern.search(content), (
        f"{SCRIPT_PATH} must set annotate_links to the Python literal True "
        "(e.g. annotate_links=True or 'annotate_links': True). Other values are not acceptable."
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


def test_output_md_preserves_first_url():
    content = _read_output_md()
    assert "https://example.com/docs" in content, (
        f"Output markdown at {OUTPUT_MD} must preserve the source URL "
        f"'https://example.com/docs' verbatim (this is what annotate_links=True is supposed to keep). "
        f"Got first 500 chars: {content[:500]!r}"
    )


def test_output_md_preserves_second_url():
    content = _read_output_md()
    assert "https://llamaindex.ai" in content, (
        f"Output markdown at {OUTPUT_MD} must preserve the source URL "
        f"'https://llamaindex.ai' verbatim (this is what annotate_links=True is supposed to keep). "
        f"Got first 500 chars: {content[:500]!r}"
    )


def test_output_md_contains_anchor_label():
    """At least one of the human-readable anchor labels from the PDF should still be present."""
    content = _read_output_md().lower()
    candidates = ["visit our docs", "llamaindex homepage"]
    found = [c for c in candidates if c in content]
    assert found, (
        f"Output markdown at {OUTPUT_MD} must contain at least one of the anchor labels "
        f"{candidates} (case-insensitive). Got first 500 chars: {content[:500]!r}"
    )
