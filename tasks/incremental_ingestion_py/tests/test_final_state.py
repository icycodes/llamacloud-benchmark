import json
import os
import subprocess

import pytest
import requests

PROJECT_DIR = "/home/user/myproject"
SCRIPT_PATH = os.path.join(PROJECT_DIR, "ingest.py")
INITIAL_DIR = os.path.join(PROJECT_DIR, "initial_docs")
NEW_DIR = os.path.join(PROJECT_DIR, "new_docs")
OUTPUT_FILE = os.path.join(PROJECT_DIR, "result.json")
TRIAL_ID_FILE = "/logs/artifacts/trial_id"
LLAMA_CLOUD_BASE_URL = "https://api.cloud.llamaindex.ai"


def _read_trial_id():
    with open(TRIAL_ID_FILE, "r", encoding="utf-8") as f:
        return f.read().strip()


def _expected_index_name():
    return f"harbor-inc-{_read_trial_id()}"


def _list_pipelines(api_key):
    response = requests.get(
        f"{LLAMA_CLOUD_BASE_URL}/api/v1/pipelines",
        headers={"Authorization": f"Bearer {api_key}"},
        params={"project_name": "Default"},
        timeout=60,
    )
    assert response.status_code == 200, (
        "LlamaCloud pipelines list returned status "
        f"{response.status_code}: {response.text}"
    )
    return response.json()


def _list_pipeline_files(api_key, pipeline_id):
    response = requests.get(
        f"{LLAMA_CLOUD_BASE_URL}/api/v1/pipelines/{pipeline_id}/files",
        headers={"Authorization": f"Bearer {api_key}"},
        params={"per_page": 200},
        timeout=60,
    )
    assert response.status_code == 200, (
        f"LlamaCloud pipeline files list for pipeline {pipeline_id} "
        f"returned status {response.status_code}: {response.text}"
    )
    return response.json()


@pytest.fixture(scope="module")
def run_script():
    """Run the user's script once for the entire module and return the result."""
    if os.path.isfile(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)

    assert os.path.isfile(SCRIPT_PATH), (
        f"Expected user-provided script at {SCRIPT_PATH}; it was not found."
    )

    result = subprocess.run(
        [
            "python3",
            "ingest.py",
            "--initial-dir",
            INITIAL_DIR,
            "--new-dir",
            NEW_DIR,
            "--output",
            OUTPUT_FILE,
        ],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
        timeout=1200,
    )
    return result


def test_script_exits_zero(run_script):
    assert run_script.returncode == 0, (
        "Expected ingest.py to exit with code 0, "
        f"got {run_script.returncode}. stdout={run_script.stdout!r} "
        f"stderr={run_script.stderr!r}"
    )


def test_stdout_contains_ingested_summary(run_script):
    expected_line = f"Ingested 2 file(s) into {_expected_index_name()}"
    stdout_lines = [line.strip() for line in run_script.stdout.splitlines()]
    assert expected_line in stdout_lines, (
        f"Expected stdout to contain the line {expected_line!r}, "
        f"got stdout lines: {stdout_lines!r}"
    )


def test_index_exists_on_llamacloud(run_script):
    """Use the LlamaCloud REST API to verify the new index/pipeline exists."""
    api_key = os.environ.get("LLAMA_CLOUD_API_KEY")
    assert api_key, "LLAMA_CLOUD_API_KEY env var is required for verification."

    pipelines = _list_pipelines(api_key)
    pipeline_names = [p.get("name") for p in pipelines]
    expected = _expected_index_name()
    assert expected in pipeline_names, (
        f"Expected pipeline named {expected!r} to exist in LlamaCloud project "
        f"'Default'; got names={pipeline_names!r}"
    )


def test_new_files_attached_to_same_pipeline(run_script):
    """The new files must be uploaded into the SAME pipeline created from the initial batch."""
    api_key = os.environ.get("LLAMA_CLOUD_API_KEY")
    assert api_key, "LLAMA_CLOUD_API_KEY env var is required for verification."

    pipelines = _list_pipelines(api_key)
    expected = _expected_index_name()
    matching = [p for p in pipelines if p.get("name") == expected]
    assert len(matching) == 1, (
        f"Expected exactly one pipeline named {expected!r} in project 'Default'; "
        f"found {len(matching)}."
    )
    pipeline_id = matching[0]["id"]

    files = _list_pipeline_files(api_key, pipeline_id)
    assert isinstance(files, list), (
        f"Expected pipeline files response to be a JSON array, got: {files!r}"
    )
    # The initial batch contains 1 document and the new batch contains 2 files,
    # so the pipeline must have at least 3 files attached.
    assert len(files) >= 3, (
        f"Expected pipeline {expected!r} to have at least 3 files attached "
        f"(1 initial + 2 incremental); got {len(files)}: {files!r}"
    )
    file_names = [f.get("name") for f in files]
    for required in ("leadership.txt", "headcount.txt"):
        assert required in file_names, (
            f"Expected file {required!r} to be attached to pipeline {expected!r}; "
            f"got file names: {file_names!r}"
        )


def test_output_json_structure(run_script):
    assert os.path.isfile(OUTPUT_FILE), (
        f"Expected output file {OUTPUT_FILE} to be created by ingest.py."
    )
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, dict), (
        f"Expected {OUTPUT_FILE} to contain a JSON object, got: {type(data).__name__}"
    )
    assert data.get("index_name") == _expected_index_name(), (
        "Expected output JSON 'index_name' to be "
        f"{_expected_index_name()!r}; got {data.get('index_name')!r}"
    )
    assert isinstance(data.get("initial_documents"), int), (
        "Expected output JSON 'initial_documents' to be an integer; "
        f"got: {data.get('initial_documents')!r}"
    )
    assert data["initial_documents"] >= 1, (
        "Expected 'initial_documents' to be >= 1 (the initial_docs folder contains "
        f"at least one document); got: {data['initial_documents']!r}"
    )
    assert data.get("uploaded_files") == ["headcount.txt", "leadership.txt"], (
        "Expected output JSON 'uploaded_files' to be exactly "
        '["headcount.txt", "leadership.txt"] (sorted, base names only); '
        f"got: {data.get('uploaded_files')!r}"
    )


def test_script_uses_required_apis():
    with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
        source = f.read()
    assert (
        "from llama_index.indices.managed.llama_cloud import LlamaCloudIndex"
        in source
    ), (
        "ingest.py must import LlamaCloudIndex from "
        "llama_index.indices.managed.llama_cloud."
    )
    assert "LlamaCloudIndex.from_documents" in source, (
        "ingest.py must call LlamaCloudIndex.from_documents to create the index."
    )
    assert "upload_file" in source, (
        "ingest.py must call index.upload_file(...) to add the new files incrementally."
    )
    assert "wait_for_completion" in source, (
        "ingest.py must call index.wait_for_completion() to block until ingestion finishes."
    )
    assert "/logs/artifacts/trial_id" in source, (
        "ingest.py must read the trial_id from /logs/artifacts/trial_id."
    )


def test_script_fails_on_missing_initial_dir():
    """The script must exit non-zero when --initial-dir does not exist."""
    missing_dir = os.path.join(PROJECT_DIR, "does_not_exist_initial_dir")
    assert not os.path.exists(missing_dir), (
        f"Test prerequisite failed: {missing_dir} should not exist."
    )
    result = subprocess.run(
        [
            "python3",
            "ingest.py",
            "--initial-dir",
            missing_dir,
            "--new-dir",
            NEW_DIR,
            "--output",
            os.path.join(PROJECT_DIR, "should_not_be_written.json"),
        ],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
        timeout=120,
    )
    assert result.returncode != 0, (
        "Expected ingest.py to exit with a non-zero status code when "
        f"--initial-dir does not exist; got returncode={result.returncode}, "
        f"stdout={result.stdout!r}, stderr={result.stderr!r}"
    )


def test_script_fails_on_missing_new_dir():
    """The script must exit non-zero when --new-dir does not exist."""
    missing_dir = os.path.join(PROJECT_DIR, "does_not_exist_new_dir")
    assert not os.path.exists(missing_dir), (
        f"Test prerequisite failed: {missing_dir} should not exist."
    )
    result = subprocess.run(
        [
            "python3",
            "ingest.py",
            "--initial-dir",
            INITIAL_DIR,
            "--new-dir",
            missing_dir,
            "--output",
            os.path.join(PROJECT_DIR, "should_not_be_written.json"),
        ],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
        timeout=120,
    )
    assert result.returncode != 0, (
        "Expected ingest.py to exit with a non-zero status code when "
        f"--new-dir does not exist; got returncode={result.returncode}, "
        f"stdout={result.stdout!r}, stderr={result.stderr!r}"
    )
