import os
import re
import subprocess

import pytest

PROJECT_DIR = "/home/user/myproject"
SCRIPT_PATH = os.path.join(PROJECT_DIR, "parse_doc.ts")
SAMPLE_PDF = os.path.join(PROJECT_DIR, "sample.pdf")
OUTPUT_MD = os.path.join(PROJECT_DIR, "output.md")
OUTPUT_LOG = os.path.join(PROJECT_DIR, "output.log")
TRIAL_ID_PATH = "/logs/artifacts/trial_id"


def _read_trial_id() -> str:
    with open(TRIAL_ID_PATH, "r", encoding="utf-8") as f:
        return f.read().strip()


@pytest.fixture(scope="session", autouse=True)
def run_agent_script():
    """Clean previously generated outputs and execute the agent's TypeScript script once."""
    assert os.path.isfile(SCRIPT_PATH), (
        f"Agent's script {SCRIPT_PATH} does not exist. The agent must create it."
    )
    assert os.path.isfile(SAMPLE_PDF), (
        f"Required sample PDF {SAMPLE_PDF} is missing."
    )

    # Cleanup any pre-existing artifacts so the test verifies fresh outputs.
    for path in (OUTPUT_MD, OUTPUT_LOG):
        if os.path.isfile(path):
            os.remove(path)

    # Run the TS file with `npx tsx` from the project directory.
    completed = subprocess.run(
        ["npx", "tsx", SCRIPT_PATH],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=300,
    )
    yield completed


def test_script_exit_code_is_zero(run_agent_script):
    """`npx tsx parse_doc.ts` must run to completion with exit code 0."""
    completed = run_agent_script
    assert completed.returncode == 0, (
        f"parse_doc.ts exited with non-zero status {completed.returncode}.\n"
        f"STDOUT:\n{completed.stdout}\n"
        f"STDERR:\n{completed.stderr}"
    )


def test_output_markdown_file_exists():
    """The parsed markdown output file must exist and be non-empty."""
    assert os.path.isfile(OUTPUT_MD), (
        f"Expected markdown output file at {OUTPUT_MD} to be created by the script."
    )
    assert os.path.getsize(OUTPUT_MD) > 0, (
        f"Markdown output file {OUTPUT_MD} exists but is empty."
    )


def test_output_markdown_contains_quarterly_sales_report():
    """The markdown content must reflect the heading present in the sample PDF."""
    with open(OUTPUT_MD, "r", encoding="utf-8") as f:
        content = f.read()
    assert "quarterly sales report" in content.lower(), (
        "Expected the parsed markdown at "
        f"{OUTPUT_MD} to contain the phrase 'Quarterly Sales Report' "
        "(case-insensitive) from the sample PDF, but it was not found.\n"
        f"First 500 chars of output.md:\n{content[:500]!r}"
    )


def test_output_log_file_exists():
    """The log file written by the script must exist and be non-empty."""
    assert os.path.isfile(OUTPUT_LOG), (
        f"Expected log file at {OUTPUT_LOG} to be created by the script."
    )
    assert os.path.getsize(OUTPUT_LOG) > 0, (
        f"Log file {OUTPUT_LOG} exists but is empty."
    )


def test_output_log_contains_trial_id_line():
    """The log file must contain `trial_id: <value>` matching the harness value."""
    trial_id = _read_trial_id()
    with open(OUTPUT_LOG, "r", encoding="utf-8") as f:
        log_content = f.read()
    pattern = re.compile(
        r"^\s*trial_id\s*:\s*" + re.escape(trial_id) + r"\s*$",
        re.MULTILINE,
    )
    assert pattern.search(log_content), (
        f"Expected {OUTPUT_LOG} to contain a line `trial_id: {trial_id}` "
        f"matching the value at {TRIAL_ID_PATH}, but no such line was found.\n"
        f"Log content:\n{log_content!r}"
    )


def test_output_log_contains_pages_parsed_line():
    """The log file must contain a `pages_parsed: <N>` line with N >= 1."""
    with open(OUTPUT_LOG, "r", encoding="utf-8") as f:
        log_content = f.read()
    match = re.search(r"^\s*pages_parsed\s*:\s*(\d+)\s*$", log_content, re.MULTILINE)
    assert match, (
        f"Expected {OUTPUT_LOG} to contain a line matching `pages_parsed: <N>` "
        f"with N a non-negative integer, but no such line was found.\n"
        f"Log content:\n{log_content!r}"
    )
    pages = int(match.group(1))
    assert pages >= 1, (
        f"Expected pages_parsed to be at least 1, got {pages}."
    )
