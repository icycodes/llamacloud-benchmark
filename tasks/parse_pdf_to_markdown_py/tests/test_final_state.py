import os
import re

import pytest
import requests

PROJECT_DIR = "/home/user/myproject"
SCRIPT_PATH = os.path.join(PROJECT_DIR, "parse_report.py")
OUTPUT_MD = os.path.join(PROJECT_DIR, "output.md")
LOG_PATH = os.path.join(PROJECT_DIR, "parse.log")
PDF_PATH = os.path.join(PROJECT_DIR, "quarterly_report.pdf")

JOB_ID_RE = re.compile(r"^Parse job ID:\s+([A-Za-z0-9\-]+)\s*$", re.MULTILINE)
PARSED_FILE_RE = re.compile(r"^Parsed file:\s+/home/user/myproject/quarterly_report\.pdf\s*$", re.MULTILINE)


def _read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def test_script_file_exists():
    assert os.path.isfile(SCRIPT_PATH), (
        f"Expected the executor to create the parse script at {SCRIPT_PATH}."
    )


def test_output_markdown_exists_and_non_empty():
    assert os.path.isfile(OUTPUT_MD), f"Expected markdown output at {OUTPUT_MD}."
    assert os.path.getsize(OUTPUT_MD) > 0, f"Markdown output {OUTPUT_MD} must not be empty."


def test_output_markdown_contains_expected_content():
    """The parsed markdown must reflect text from the original PDF (round-trip evidence)."""
    content = _read_text(OUTPUT_MD)
    lowered = content.lower()
    assert "acme corp quarterly report" in lowered, (
        "Expected the parsed markdown to contain the document title "
        "'ACME CORP QUARTERLY REPORT', but it was not found in output.md."
    )
    assert "12345" in content, (
        "Expected the parsed markdown to contain the revenue figure '12345' "
        "from the source PDF, but it was not found in output.md."
    )


def test_parse_log_exists():
    assert os.path.isfile(LOG_PATH), f"Expected log file at {LOG_PATH}."


def test_parse_log_lines_present():
    content = _read_text(LOG_PATH)
    assert JOB_ID_RE.search(content), (
        "Expected parse.log to contain a line matching '^Parse job ID: <id>$', "
        f"got:\n{content}"
    )
    assert PARSED_FILE_RE.search(content), (
        "Expected parse.log to contain a line matching "
        "'^Parsed file: /home/user/myproject/quarterly_report.pdf$', "
        f"got:\n{content}"
    )


def test_parse_job_completed_via_llamacloud_api():
    """Confirm the parse job exists on LlamaCloud and has reached a successful terminal state."""
    assert os.path.isfile(LOG_PATH), f"Cannot validate job; log file {LOG_PATH} missing."
    content = _read_text(LOG_PATH)
    match = JOB_ID_RE.search(content)
    assert match, "Could not extract a Parse job ID from parse.log."
    job_id = match.group(1)

    api_key = os.environ.get("LLAMA_CLOUD_API_KEY")
    assert api_key, "LLAMA_CLOUD_API_KEY must be set in the verifier environment."

    base_url = os.environ.get("LLAMA_CLOUD_BASE_URL", "https://api.cloud.llamaindex.ai")
    url = f"{base_url.rstrip('/')}/api/v2/parse/{job_id}"
    response = requests.get(
        url,
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        timeout=60,
    )
    assert response.status_code == 200, (
        f"Failed to retrieve parse job {job_id} from LlamaCloud: "
        f"HTTP {response.status_code} body={response.text!r}"
    )
    payload = response.json()
    assert payload.get("id") == job_id, (
        f"LlamaCloud returned a job with id {payload.get('id')!r}, "
        f"expected {job_id!r}."
    )
    status = str(payload.get("status", "")).upper()
    assert status in {"COMPLETED", "SUCCESS"}, (
        f"Expected parse job {job_id} to be in a successful terminal state, "
        f"got status={status!r} (full payload keys: {list(payload.keys())})."
    )
