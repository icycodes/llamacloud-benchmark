import os
import re
import subprocess

import pytest
import requests

PROJECT_DIR = "/home/user/myproject"
SCRIPT_PATH = os.path.join(PROJECT_DIR, "parse.sh")
SAMPLE_PDF = os.path.join(PROJECT_DIR, "sample.pdf")
OUTPUT_MD = os.path.join(PROJECT_DIR, "sample.md")
MISSING_PDF = os.path.join(PROJECT_DIR, "does_not_exist.pdf")

LLAMA_CLOUD_BASE_URL = "https://api.cloud.llamaindex.ai"

# The expected stdout line follows the format `Parsed job: <job_id>` where the
# job id is a non-empty token comprised of letters, digits, `_`, and `-`.
JOB_ID_LINE_RE = re.compile(r"^Parsed job:\s+([A-Za-z0-9_-]+)\s*$")


@pytest.fixture(scope="module")
def run_parse_script():
    # Pre-cleanup: remove the markdown output if a previous run left it behind.
    if os.path.exists(OUTPUT_MD):
        os.remove(OUTPUT_MD)

    env = os.environ.copy()
    result = subprocess.run(
        ["bash", "parse.sh", "--input", SAMPLE_PDF, "--output", OUTPUT_MD],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
        env=env,
        timeout=600,
    )
    return result


@pytest.fixture(scope="module")
def parsed_job_id(run_parse_script):
    """Extract and return the job id from the script's stdout."""
    result = run_parse_script
    assert result.returncode == 0, (
        f"`bash parse.sh ...` exited with non-zero status {result.returncode}.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    job_id = None
    for line in result.stdout.splitlines():
        m = JOB_ID_LINE_RE.match(line.strip())
        if m:
            job_id = m.group(1)
            break
    assert job_id, (
        "Expected stdout to include exactly one line matching `^Parsed job: <job_id>$`. "
        f"Actual stdout: {result.stdout!r}"
    )
    return job_id


def test_parse_script_exists():
    assert os.path.isfile(SCRIPT_PATH), \
        f"Expected the parse.sh CLI script at {SCRIPT_PATH}, but it does not exist."


def test_parse_script_invokes_curl():
    with open(SCRIPT_PATH, "r", encoding="utf-8") as fh:
        contents = fh.read()
    assert "curl" in contents, \
        "parse.sh must invoke `curl` to call the LlamaCloud REST API."


def test_parse_script_references_files_endpoint():
    with open(SCRIPT_PATH, "r", encoding="utf-8") as fh:
        contents = fh.read()
    assert "api/v1/files" in contents, \
        "parse.sh must reference the file-upload endpoint `https://api.cloud.llamaindex.ai/api/v1/files/`."


def test_parse_script_references_parse_endpoint():
    with open(SCRIPT_PATH, "r", encoding="utf-8") as fh:
        contents = fh.read()
    assert "api/v2/parse" in contents, \
        "parse.sh must reference the parse endpoint `https://api.cloud.llamaindex.ai/api/v2/parse`."


def test_parse_script_requests_markdown_full_expand():
    with open(SCRIPT_PATH, "r", encoding="utf-8") as fh:
        contents = fh.read()
    assert "markdown_full" in contents, \
        "parse.sh must request `markdown_full` via the `expand` query parameter on the parse-status endpoint."


def test_parse_script_uses_cost_effective_tier():
    with open(SCRIPT_PATH, "r", encoding="utf-8") as fh:
        contents = fh.read()
    assert "cost_effective" in contents, \
        "parse.sh must use the `cost_effective` tier when submitting the parse job."


def test_parse_script_uses_latest_version():
    with open(SCRIPT_PATH, "r", encoding="utf-8") as fh:
        contents = fh.read()
    # Be lenient about whitespace/punctuation between `version` and `latest` so
    # that both `\"version\": \"latest\"` and `version=latest` are accepted.
    assert re.search(r"version[^A-Za-z0-9]{0,10}latest", contents), \
        "parse.sh must submit the parse job with `version: \"latest\"`."


def test_parse_script_does_not_use_python_sdk():
    with open(SCRIPT_PATH, "r", encoding="utf-8") as fh:
        contents = fh.read()
    forbidden = [
        "from llama_cloud",
        "from llama_parse",
        "import llama_cloud",
        "@llamaindex/llama-cloud",
        "llama-parse",
    ]
    for needle in forbidden:
        assert needle not in contents, \
            (f"parse.sh must not import or reference the LlamaCloud SDK; "
             f"found forbidden substring {needle!r} in the script.")


def test_parse_script_runs_successfully(run_parse_script):
    result = run_parse_script
    assert result.returncode == 0, (
        f"`bash parse.sh ...` exited with non-zero status {result.returncode}.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )


def test_stdout_contains_parsed_job_line(parsed_job_id):
    assert parsed_job_id, \
        "Expected stdout to contain a `Parsed job: <job_id>` line with a non-empty job id."


def test_output_markdown_file_created(run_parse_script):
    assert os.path.isfile(OUTPUT_MD), \
        f"Expected output markdown file at {OUTPUT_MD}, but it was not created."


def test_output_markdown_file_nonempty(run_parse_script):
    size = os.path.getsize(OUTPUT_MD)
    assert size > 0, f"Output markdown file {OUTPUT_MD} is empty (size={size})."


def test_output_markdown_contains_hello_llamaparse(run_parse_script):
    with open(OUTPUT_MD, "r", encoding="utf-8") as fh:
        contents = fh.read()
    assert "hello llamaparse" in contents.lower(), (
        f"Expected the parsed markdown to contain 'Hello LlamaParse' (case-insensitive); "
        f"got content (first 500 chars): {contents[:500]!r}"
    )


def test_output_markdown_contains_harbor_test_document(run_parse_script):
    with open(OUTPUT_MD, "r", encoding="utf-8") as fh:
        contents = fh.read()
    assert "harbor test document" in contents.lower(), (
        f"Expected the parsed markdown to contain 'Harbor Test Document' (case-insensitive); "
        f"got content (first 500 chars): {contents[:500]!r}"
    )


def test_parse_job_visible_via_rest_api(parsed_job_id):
    """Use the LlamaCloud REST API directly to confirm the parse job exists and
    completed with `markdown_full` containing the expected substring."""
    api_key = os.environ.get("LLAMA_CLOUD_API_KEY")
    assert api_key, "LLAMA_CLOUD_API_KEY must be set in the verifier environment."

    url = f"{LLAMA_CLOUD_BASE_URL}/api/v2/parse/{parsed_job_id}"
    response = requests.get(
        url,
        params={"expand": "markdown_full"},
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=60,
    )
    assert response.status_code == 200, (
        f"Expected HTTP 200 when fetching parse job {parsed_job_id} via the REST API; "
        f"got {response.status_code}. Body: {response.text[:500]!r}"
    )
    data = response.json()
    job = data.get("job") or {}
    assert job.get("id") == parsed_job_id, (
        f"Expected job.id == {parsed_job_id!r} in the REST API response, but got "
        f"{job.get('id')!r}. Full body: {data!r}"
    )
    assert job.get("status") == "COMPLETED", (
        f"Expected parse job {parsed_job_id} to have status 'COMPLETED' on LlamaCloud; "
        f"got {job.get('status')!r}. Full body: {data!r}"
    )
    markdown_full = data.get("markdown_full") or ""
    assert isinstance(markdown_full, str) and markdown_full.strip(), (
        f"Expected `markdown_full` to be a non-empty string in the REST API response; "
        f"got: {type(markdown_full).__name__} of length {len(markdown_full)}."
    )
    assert "hello llamaparse" in markdown_full.lower(), (
        f"Expected `markdown_full` to contain 'Hello LlamaParse' (case-insensitive); "
        f"first 500 chars: {markdown_full[:500]!r}"
    )


def test_script_fails_on_missing_input():
    # Ensure the missing path truly does not exist.
    if os.path.exists(MISSING_PDF):
        os.remove(MISSING_PDF)
    env = os.environ.copy()
    result = subprocess.run(
        ["bash", "parse.sh", "--input", MISSING_PDF, "--output", "/tmp/should_not_be_created.md"],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
        env=env,
        timeout=120,
    )
    assert result.returncode != 0, (
        f"parse.sh must exit with a non-zero status when --input refers to a missing file; "
        f"got returncode=0 with stdout: {result.stdout!r}, stderr: {result.stderr!r}"
    )
