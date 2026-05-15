import os
import re
import subprocess

import pytest

PROJECT_DIR = "/home/user/parse_task_ts"
PARSE_SCRIPT = os.path.join(PROJECT_DIR, "parse.ts")
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
    """Run `npx tsx parse.ts` once and yield the resulting output markdown text."""
    assert os.path.isfile(PARSE_SCRIPT), (
        f"Expected the executor-created script at {PARSE_SCRIPT}, but it is missing."
    )

    # Ensure output is freshly produced.
    if os.path.exists(OUTPUT_MD):
        os.remove(OUTPUT_MD)

    env = os.environ.copy()
    result = subprocess.run(
        ["npx", "tsx", "parse.ts"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        env=env,
        timeout=600,
    )
    assert result.returncode == 0, (
        "'npx tsx parse.ts' did not exit with status 0.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )

    assert os.path.isfile(OUTPUT_MD), (
        f"Expected output markdown at {OUTPUT_MD} after running parse.ts, but it is missing."
    )

    with open(OUTPUT_MD, "rb") as fp:
        raw = fp.read()
    assert len(raw) > 0, f"Output markdown {OUTPUT_MD} is empty."

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        pytest.fail(f"Output markdown {OUTPUT_MD} is not valid UTF-8: {exc}")
    return text


def test_parse_script_uses_llama_cloud_ts_sdk():
    """The script must use the LlamaCloud TypeScript SDK."""
    assert os.path.isfile(PARSE_SCRIPT), f"Missing script {PARSE_SCRIPT}."
    with open(PARSE_SCRIPT, "r", encoding="utf-8", errors="ignore") as fp:
        source = fp.read()
    assert "@llamaindex/llama-cloud" in source, (
        "parse.ts must reference the '@llamaindex/llama-cloud' SDK "
        "(e.g. import LlamaCloud from '@llamaindex/llama-cloud')."
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
