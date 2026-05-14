import os
import subprocess
import pytest

PROJECT_DIR = "/home/user/llama_task"
SCRIPT_PATH = os.path.join(PROJECT_DIR, "parse_and_retrieve.py")
OUTPUT_MD = os.path.join(PROJECT_DIR, "output.md")
OUTPUT_TXT = os.path.join(PROJECT_DIR, "output.txt")
JOB_ID_FILE = os.path.join(PROJECT_DIR, "job_id.txt")

EXPECTED_TITLE = "quarterly sales report"
EXPECTED_PRODUCTS = ["widget", "gadget", "sprocket"]


def _read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def test_parse_script_exists():
    assert os.path.isfile(SCRIPT_PATH), (
        f"Expected the user's script at {SCRIPT_PATH}, but it was not found."
    )


def test_parse_script_uses_llama_cloud_sdk():
    content = _read(SCRIPT_PATH)
    assert "from llama_cloud import LlamaCloud" in content, (
        f"{SCRIPT_PATH} must contain 'from llama_cloud import LlamaCloud' to import "
        "the LlamaCloud SDK client."
    )


def test_parse_script_invokes_parsing_parse_exactly_once():
    content = _read(SCRIPT_PATH)
    # Exactly one parse call; multiple parses would mean the agent re-parsed
    # instead of using parsing.get() to retrieve text from the same job.
    occurrences = content.count("parsing.parse(")
    assert occurrences == 1, (
        f"{SCRIPT_PATH} must invoke client.parsing.parse(...) exactly once "
        f"(found {occurrences} occurrences). The plain text MUST come from "
        f"client.parsing.get(...), not from a second parse call."
    )


def test_parse_script_invokes_parsing_get():
    content = _read(SCRIPT_PATH)
    assert "parsing.get(" in content, (
        f"{SCRIPT_PATH} must invoke client.parsing.get(...) to retrieve the text "
        f"representation of the same job without re-parsing."
    )


def test_parse_script_does_not_hardcode_api_key():
    content = _read(SCRIPT_PATH)
    assert "llx-" not in content, (
        f"{SCRIPT_PATH} appears to hardcode a LlamaCloud API key (found 'llx-' "
        f"prefix). The script must rely on the LLAMA_CLOUD_API_KEY environment "
        f"variable."
    )


def test_output_md_exists_and_nonempty():
    assert os.path.isfile(OUTPUT_MD), (
        f"Expected the parsed markdown output at {OUTPUT_MD}, but it was not found."
    )
    assert os.path.getsize(OUTPUT_MD) > 0, (
        f"Output file {OUTPUT_MD} exists but is empty. LlamaParse should produce "
        f"non-empty markdown."
    )


def test_output_md_contains_report_title():
    content = _read(OUTPUT_MD).lower()
    assert EXPECTED_TITLE in content, (
        f"Output markdown at {OUTPUT_MD} must contain the report title "
        f"'Quarterly Sales Report' (case-insensitive). First 500 chars: "
        f"{content[:500]!r}"
    )


def test_output_md_contains_at_least_one_product():
    content = _read(OUTPUT_MD).lower()
    found = [p for p in EXPECTED_PRODUCTS if p in content]
    assert found, (
        f"Output markdown at {OUTPUT_MD} must contain at least one of the source "
        f"PDF products {EXPECTED_PRODUCTS} (case-insensitive). First 500 chars: "
        f"{content[:500]!r}"
    )


def test_output_txt_exists_and_nonempty():
    assert os.path.isfile(OUTPUT_TXT), (
        f"Expected the plain-text output at {OUTPUT_TXT}, but it was not found."
    )
    assert os.path.getsize(OUTPUT_TXT) > 0, (
        f"Output file {OUTPUT_TXT} exists but is empty. The text retrieved via "
        f"client.parsing.get(job_id=..., expand=['text_full']) should be non-empty."
    )


def test_output_txt_contains_report_title():
    content = _read(OUTPUT_TXT).lower()
    assert EXPECTED_TITLE in content, (
        f"Output text at {OUTPUT_TXT} must contain the report title "
        f"'Quarterly Sales Report' (case-insensitive). First 500 chars: "
        f"{content[:500]!r}"
    )


def test_output_txt_contains_at_least_one_product():
    content = _read(OUTPUT_TXT).lower()
    found = [p for p in EXPECTED_PRODUCTS if p in content]
    assert found, (
        f"Output text at {OUTPUT_TXT} must contain at least one of the source PDF "
        f"products {EXPECTED_PRODUCTS} (case-insensitive). First 500 chars: "
        f"{content[:500]!r}"
    )


def test_job_id_file_exists_and_nonempty():
    assert os.path.isfile(JOB_ID_FILE), (
        f"Expected job id file at {JOB_ID_FILE}, but it was not found."
    )
    job_id = _read(JOB_ID_FILE).strip()
    assert len(job_id) >= 8, (
        f"{JOB_ID_FILE} must contain a non-empty job id string of at least 8 "
        f"characters. Got: {job_id!r}"
    )


def test_job_id_is_resolvable_via_llama_cloud_sdk():
    """Priority 1: Use the LlamaCloud SDK to confirm the recorded job_id was
    produced by a real, completed parse job on the LlamaCloud server."""
    job_id = _read(JOB_ID_FILE).strip()
    code = (
        "import sys\n"
        "from llama_cloud import LlamaCloud\n"
        "client = LlamaCloud()\n"
        f"job_id = {job_id!r}\n"
        "result = client.parsing.get(job_id=job_id, expand=['job_metadata'])\n"
        "status = getattr(result.job, 'status', None)\n"
        "print('JOB_ID=' + result.job.id)\n"
        "print('STATUS=' + str(status))\n"
    )
    result = subprocess.run(
        ["python3", "-c", code],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, (
        f"client.parsing.get(job_id={job_id!r}, expand=['job_metadata']) failed. "
        f"This indicates the job id recorded in {JOB_ID_FILE} is not recognized "
        f"by the LlamaCloud server. stderr: {result.stderr}"
    )
    assert f"JOB_ID={job_id}" in result.stdout, (
        f"LlamaCloud returned a job id that does not match the one recorded in "
        f"{JOB_ID_FILE}. Expected {job_id!r}. stdout: {result.stdout!r}"
    )
