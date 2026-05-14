import os
import subprocess
import pytest

PROJECT_DIR = "/home/user/llama_task"
SCRIPT_PATH = os.path.join(PROJECT_DIR, "parse_report.py")
OUTPUT_MD = os.path.join(PROJECT_DIR, "output.md")


def test_parse_script_exists():
    assert os.path.isfile(SCRIPT_PATH), (
        f"Expected the user's parsing script at {SCRIPT_PATH}, but it was not found."
    )


def test_parse_script_uses_llama_cloud_sdk():
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


def test_parse_script_does_not_hardcode_api_key():
    with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    # The key should come from environment, not be hardcoded as a literal "llx-..." string in the script.
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


def test_output_md_contains_report_title():
    with open(OUTPUT_MD, "r", encoding="utf-8") as f:
        content = f.read()
    lowered = content.lower()
    assert "quarterly sales report" in lowered, (
        f"Output markdown at {OUTPUT_MD} must contain the report title "
        f"'Quarterly Sales Report' (case-insensitive). Got first 500 chars: {content[:500]!r}"
    )


def test_output_md_contains_at_least_one_product():
    with open(OUTPUT_MD, "r", encoding="utf-8") as f:
        content = f.read()
    lowered = content.lower()
    products = ["widget", "gadget", "sprocket"]
    found = [p for p in products if p in lowered]
    assert found, (
        f"Output markdown at {OUTPUT_MD} must contain at least one of the source PDF "
        f"products {products} (case-insensitive). Got first 500 chars: {content[:500]!r}"
    )
