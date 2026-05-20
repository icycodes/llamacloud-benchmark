import json
import os
import re

import pytest
import requests

PROJECT_DIR = "/home/user/myproject"
LOG_FILE = os.path.join(PROJECT_DIR, "output.log")
TRIAL_ID_PATH = "/logs/artifacts/trial_id"
LLAMA_CLOUD_BASE_URL = "https://api.cloud.llamaindex.ai"


@pytest.fixture(scope="module")
def trial_id():
    assert os.path.isfile(TRIAL_ID_PATH), (
        f"trial_id artifact is missing at {TRIAL_ID_PATH}."
    )
    with open(TRIAL_ID_PATH) as f:
        value = f.read().strip()
    assert value, "trial_id artifact is empty."
    return value


@pytest.fixture(scope="module")
def expected_index_name(trial_id):
    return f"harbor-ts-index-{trial_id}"


@pytest.fixture(scope="module")
def log_contents():
    assert os.path.isfile(LOG_FILE), f"Expected log file at {LOG_FILE}, but it is missing."
    with open(LOG_FILE) as f:
        return f.read()


@pytest.fixture(scope="module")
def llama_cloud_headers():
    api_key = os.environ.get("LLAMA_CLOUD_API_KEY")
    assert api_key, "LLAMA_CLOUD_API_KEY env var must be set for the verifier."
    return {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }


def test_index_source_file_exists():
    src_path = os.path.join(PROJECT_DIR, "index.ts")
    assert os.path.isfile(src_path), (
        f"Expected the executor-created TypeScript entrypoint at {src_path}."
    )


def test_log_contains_index_name_line(log_contents, expected_index_name):
    expected_line = f"Index name: {expected_index_name}"
    assert expected_line in log_contents, (
        f"Expected log file to contain '{expected_line}'. Got:\n{log_contents}"
    )


def test_log_contains_query_line(log_contents):
    expected = "Query: What is the capital of France?"
    assert expected in log_contents, (
        f"Expected log file to contain a line '{expected}'. Got:\n{log_contents}"
    )


def test_log_contains_answer_mentioning_paris(log_contents):
    match = re.search(r"^Answer:\s*(.+)$", log_contents, flags=re.MULTILINE)
    assert match is not None, (
        "Expected a line starting with 'Answer: ' in output.log, but none was found."
    )
    answer = match.group(1).strip()
    assert answer, "The 'Answer:' line was present but the answer text was empty."
    assert "paris" in answer.lower(), (
        f"Expected the model's answer to mention 'Paris' (case-insensitive). Got: {answer!r}"
    )


def test_log_contains_summary_json(log_contents, expected_index_name):
    match = re.search(r"^Summary:\s*(\{.*\})\s*$", log_contents, flags=re.MULTILINE)
    assert match is not None, (
        "Expected a final line of the form 'Summary: {<json>}' in output.log."
    )
    try:
        summary = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"The Summary line is not valid JSON: {match.group(1)!r} ({exc})"
        )
    assert summary.get("index_name") == expected_index_name, (
        f"Summary.index_name must equal {expected_index_name!r}, got {summary.get('index_name')!r}."
    )
    assert summary.get("num_documents") == 3, (
        f"Summary.num_documents must equal 3, got {summary.get('num_documents')!r}."
    )


def test_pipeline_exists_in_llama_cloud(llama_cloud_headers, expected_index_name):
    """Verify via the LlamaCloud REST API that a pipeline with the expected name was created."""
    url = f"{LLAMA_CLOUD_BASE_URL}/api/v1/pipelines"
    response = requests.get(
        url,
        headers=llama_cloud_headers,
        params={"project_name": "Default"},
        timeout=60,
    )
    assert response.status_code == 200, (
        f"LlamaCloud pipelines list call failed with status "
        f"{response.status_code}: {response.text}"
    )
    pipelines = response.json()
    names = [p.get("name") for p in pipelines]
    assert expected_index_name in names, (
        f"Expected to find a LlamaCloud pipeline named {expected_index_name!r} in project 'Default'. "
        f"Found: {names}"
    )


def test_pipeline_has_ingested_documents(llama_cloud_headers, expected_index_name):
    """Verify that the created pipeline has at least 3 ingested files."""
    list_url = f"{LLAMA_CLOUD_BASE_URL}/api/v1/pipelines"
    response = requests.get(
        list_url,
        headers=llama_cloud_headers,
        params={"project_name": "Default"},
        timeout=60,
    )
    assert response.status_code == 200, (
        f"LlamaCloud pipelines list call failed: {response.status_code} {response.text}"
    )
    pipelines = response.json()
    matching = [p for p in pipelines if p.get("name") == expected_index_name]
    assert matching, (
        f"Pipeline {expected_index_name!r} not found when checking ingested files."
    )
    pipeline_id = matching[0].get("id")
    assert pipeline_id, f"Matching pipeline is missing an 'id' field: {matching[0]!r}"

    files_url = f"{LLAMA_CLOUD_BASE_URL}/api/v1/pipelines/{pipeline_id}/files"
    files_response = requests.get(files_url, headers=llama_cloud_headers, timeout=60)
    assert files_response.status_code == 200, (
        f"Failed to list files for pipeline {pipeline_id}: "
        f"{files_response.status_code} {files_response.text}"
    )
    files = files_response.json()
    assert isinstance(files, list), (
        f"Expected pipeline files endpoint to return a list, got {type(files).__name__}: {files!r}"
    )
    assert len(files) >= 3, (
        f"Expected at least 3 ingested files in pipeline {expected_index_name!r}, "
        f"got {len(files)}."
    )
