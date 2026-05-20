import os
import re
import subprocess

import pytest

PROJECT_DIR = "/home/user/parse_task"
PARSE_SCRIPT = os.path.join(PROJECT_DIR, "parse.py")
OUTPUT_MD = os.path.join(PROJECT_DIR, "output.md")

EXPECTED_KEYWORDS = [
    "Quarterly Revenue Report",
    "Total revenue for Q3 was $1,234,567",
    "Engineering",
    "Marketing",
    "Sales",
    "Operations",
]


@pytest.fixture(scope="module")
def parsed_output():
    """Run parse.py once and yield the output markdown text."""
    assert os.path.isfile(PARSE_SCRIPT), (
        f"Expected the executor-created script at {PARSE_SCRIPT}, but it is missing."
    )

    # Ensure output is freshly produced.
    if os.path.exists(OUTPUT_MD):
        os.remove(OUTPUT_MD)

    env = os.environ.copy()
    result = subprocess.run(
        ["python3", "parse.py"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        env=env,
        timeout=600,
    )
    assert result.returncode == 0, (
        "parse.py did not exit with status 0.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )

    assert os.path.isfile(OUTPUT_MD), (
        f"Expected output markdown at {OUTPUT_MD} after running parse.py, but it is missing."
    )

    with open(OUTPUT_MD, "rb") as fp:
        raw = fp.read()
    assert len(raw) > 0, f"Output markdown {OUTPUT_MD} is empty."

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        pytest.fail(f"Output markdown {OUTPUT_MD} is not valid UTF-8: {exc}")
    return text


def test_parse_script_uses_llama_cloud_sdk():
    """The script must import the LlamaCloud Python SDK."""
    assert os.path.isfile(PARSE_SCRIPT), (
        f"Missing script {PARSE_SCRIPT}."
    )
    with open(PARSE_SCRIPT, "r", encoding="utf-8", errors="ignore") as fp:
        source = fp.read()
    pattern = re.compile(r"(from\s+llama_cloud|import\s+llama_cloud)", re.IGNORECASE)
    assert pattern.search(source), (
        "parse.py must import the llama_cloud SDK (e.g. 'from llama_cloud import LlamaCloud')."
    )


@pytest.mark.parametrize("keyword", EXPECTED_KEYWORDS)
def test_output_contains_expected_keyword(parsed_output, keyword):
    lowered = parsed_output.lower()
    assert keyword.lower() in lowered, (
        f"Expected substring '{keyword}' to appear in {OUTPUT_MD}, but it was not found.\n"
        f"First 500 chars of output: {parsed_output[:500]!r}"
    )


def test_output_contains_markdown_table(parsed_output):
    """Markdown tables use '|' separators; require at least two lines containing '|'."""
    lines_with_pipe = [ln for ln in parsed_output.splitlines() if "|" in ln]
    assert len(lines_with_pipe) >= 2, (
        "Output markdown does not appear to contain a markdown-formatted table "
        f"(found {len(lines_with_pipe)} lines containing '|'). "
        f"First 800 chars: {parsed_output[:800]!r}"
    )
