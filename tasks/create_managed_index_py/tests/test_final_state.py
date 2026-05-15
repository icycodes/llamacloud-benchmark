import os
import subprocess

import pytest
import requests

PROJECT_DIR = "/home/user/myproject"
SCRIPT_PATH = os.path.join(PROJECT_DIR, "build_index.py")
DATA_DIR = os.path.join(PROJECT_DIR, "docs")
OUTPUT_FILE = os.path.join(PROJECT_DIR, "answer.txt")
TRIAL_ID_FILE = "/logs/artifacts/trial_id"
LLAMA_CLOUD_BASE_URL = "https://api.cloud.llamaindex.ai"
QUERY = "In what year was Acme Widgets Corporation founded?"


def _read_trial_id():
    with open(TRIAL_ID_FILE, "r", encoding="utf-8") as f:
        return f.read().strip()


def _expected_index_name():
    return f"harbor-rag-{_read_trial_id()}"


@pytest.fixture(scope="module")
def run_script():
    """Run the user's script once for the entire module and return the result."""
    # Cleanup any pre-existing output file
    if os.path.isfile(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)

    assert os.path.isfile(SCRIPT_PATH), (
        f"Expected user-provided script at {SCRIPT_PATH}; it was not found."
    )

    result = subprocess.run(
        [
            "python3",
            "build_index.py",
            "--data-dir",
            DATA_DIR,
            "--query",
            QUERY,
            "--output",
            OUTPUT_FILE,
        ],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
        timeout=900,
    )
    return result


def test_script_exits_zero(run_script):
    assert run_script.returncode == 0, (
        "Expected build_index.py to exit with code 0, "
        f"got {run_script.returncode}. stdout={run_script.stdout!r} "
        f"stderr={run_script.stderr!r}"
    )


def test_stdout_contains_index_name(run_script):
    expected_line = f"Index name: {_expected_index_name()}"
    stdout_lines = [line.strip() for line in run_script.stdout.splitlines()]
    assert expected_line in stdout_lines, (
        f"Expected stdout to contain the line {expected_line!r}, "
        f"got stdout lines: {stdout_lines!r}"
    )


def test_index_exists_on_llamacloud(run_script):
    """Use the LlamaCloud REST API to verify the new index/pipeline exists."""
    api_key = os.environ.get("LLAMA_CLOUD_API_KEY")
    assert api_key, "LLAMA_CLOUD_API_KEY env var is required for verification."

    url = f"{LLAMA_CLOUD_BASE_URL}/api/v1/pipelines"
    response = requests.get(
        url,
        headers={"Authorization": f"Bearer {api_key}"},
        params={"project_name": "Default"},
        timeout=60,
    )
    assert response.status_code == 200, (
        f"LlamaCloud pipelines list returned status "
        f"{response.status_code}: {response.text}"
    )
    pipelines = response.json()
    assert isinstance(pipelines, list), (
        f"Expected pipelines list response to be a JSON array, got: {pipelines!r}"
    )
    pipeline_names = [p.get("name") for p in pipelines]
    expected = _expected_index_name()
    assert expected in pipeline_names, (
        f"Expected pipeline named {expected!r} to exist in LlamaCloud project "
        f"'Default'; got names={pipeline_names!r}"
    )


def test_output_file_exists_and_non_empty(run_script):
    assert os.path.isfile(OUTPUT_FILE), (
        f"Expected output file {OUTPUT_FILE} to be created by build_index.py."
    )
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    assert content.strip(), (
        f"Output file {OUTPUT_FILE} exists but is empty; expected a non-empty answer."
    )


def test_output_file_contains_founding_year(run_script):
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    assert "1957" in content, (
        "Expected the query response to mention the founding year '1957'. "
        f"Actual response: {content!r}"
    )


def test_script_imports_managed_index():
    with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
        source = f.read()
    assert "from llama_index.indices.managed.llama_cloud import LlamaCloudIndex" in source, (
        "build_index.py must import LlamaCloudIndex from "
        "llama_index.indices.managed.llama_cloud."
    )
    assert "LlamaCloudIndex.from_documents" in source, (
        "build_index.py must call LlamaCloudIndex.from_documents to create the managed index."
    )
    assert 'project_name="Default"' in source or "project_name='Default'" in source, (
        "build_index.py must pass project_name=\"Default\" to LlamaCloudIndex.from_documents."
    )
    assert "/logs/artifacts/trial_id" in source, (
        "build_index.py must read the trial_id from /logs/artifacts/trial_id."
    )


def test_script_fails_on_missing_data_dir():
    """The script must exit non-zero when --data-dir does not exist."""
    missing_dir = os.path.join(PROJECT_DIR, "does_not_exist_dir")
    # Make sure it really does not exist.
    assert not os.path.exists(missing_dir), (
        f"Test prerequisite failed: {missing_dir} should not exist."
    )
    result = subprocess.run(
        [
            "python3",
            "build_index.py",
            "--data-dir",
            missing_dir,
            "--query",
            "anything",
            "--output",
            os.path.join(PROJECT_DIR, "should_not_be_written.txt"),
        ],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
        timeout=120,
    )
    assert result.returncode != 0, (
        "Expected build_index.py to exit with a non-zero status code when "
        f"--data-dir does not exist; got returncode={result.returncode}, "
        f"stdout={result.stdout!r}, stderr={result.stderr!r}"
    )
