import json
import os
import subprocess

import pytest
import requests

PROJECT_DIR = "/home/user/myproject"
SCRIPT_PATH = os.path.join(PROJECT_DIR, "chat.py")
DATA_DIR = os.path.join(PROJECT_DIR, "docs")
OUTPUT_FILE = os.path.join(PROJECT_DIR, "transcript.json")
TRIAL_ID_FILE = "/logs/artifacts/trial_id"
LLAMA_CLOUD_BASE_URL = "https://api.cloud.llamaindex.ai"
MESSAGE_1 = "In what year was Acme Widgets Corporation founded?"
MESSAGE_2 = "Who is the current CEO of that company?"


def _read_trial_id():
    with open(TRIAL_ID_FILE, "r", encoding="utf-8") as f:
        return f.read().strip()


def _expected_index_name():
    return f"harbor-chat-{_read_trial_id()}"


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
            "chat.py",
            "--data-dir",
            DATA_DIR,
            "--message1",
            MESSAGE_1,
            "--message2",
            MESSAGE_2,
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
        "Expected chat.py to exit with code 0, "
        f"got {run_script.returncode}. stdout={run_script.stdout!r} "
        f"stderr={run_script.stderr!r}"
    )


def test_stdout_contains_chat_session_line(run_script):
    expected_line = f"Chat session: {_expected_index_name()}"
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


def test_output_file_is_valid_json(run_script):
    assert os.path.isfile(OUTPUT_FILE), (
        f"Expected output file {OUTPUT_FILE} to be created by chat.py."
    )
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(
                f"Output file {OUTPUT_FILE} is not valid JSON: {e}"
            )
    assert isinstance(data, dict), (
        f"Expected the output JSON to be a JSON object, got {type(data).__name__}."
    )


def _load_output():
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def test_output_index_name_matches(run_script):
    data = _load_output()
    expected = _expected_index_name()
    assert data.get("index_name") == expected, (
        f"Expected output.index_name == {expected!r}, got {data.get('index_name')!r}."
    )


def test_output_messages_match_input(run_script):
    data = _load_output()
    assert data.get("message1") == MESSAGE_1, (
        f"Expected output.message1 to equal {MESSAGE_1!r}, "
        f"got {data.get('message1')!r}."
    )
    assert data.get("message2") == MESSAGE_2, (
        f"Expected output.message2 to equal {MESSAGE_2!r}, "
        f"got {data.get('message2')!r}."
    )


def test_response1_contains_founding_year(run_script):
    data = _load_output()
    response1 = data.get("response1")
    assert isinstance(response1, str) and response1.strip(), (
        f"Expected output.response1 to be a non-empty string, got {response1!r}."
    )
    assert "1957" in response1, (
        "Expected the response to the first chat turn to mention the founding "
        f"year '1957' (per docs/company_profile.txt). Actual response1: {response1!r}"
    )


def test_response2_uses_conversation_memory(run_script):
    """response2 must answer the follow-up correctly using conversation context."""
    data = _load_output()
    response2 = data.get("response2")
    assert isinstance(response2, str) and response2.strip(), (
        f"Expected output.response2 to be a non-empty string, got {response2!r}."
    )
    assert "Alice Thompson" in response2, (
        "Expected the response to the second chat turn to mention the CEO "
        "'Alice Thompson' (per docs/company_profile.txt). Because message2 uses "
        "the anaphoric phrase 'that company', the chat engine can only answer "
        f"correctly if it retained conversation memory. Actual response2: {response2!r}"
    )


def test_script_uses_managed_chat_engine():
    with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
        source = f.read()
    assert "from llama_index.indices.managed.llama_cloud import LlamaCloudIndex" in source, (
        "chat.py must import LlamaCloudIndex from "
        "llama_index.indices.managed.llama_cloud."
    )
    assert "LlamaCloudIndex.from_documents" in source, (
        "chat.py must call LlamaCloudIndex.from_documents to create the managed index."
    )
    assert (
        'project_name="Default"' in source or "project_name='Default'" in source
    ), (
        "chat.py must pass project_name=\"Default\" to LlamaCloudIndex.from_documents."
    )
    assert (
        'as_chat_engine(chat_mode="context"' in source
        or "as_chat_engine(chat_mode='context'" in source
    ), (
        "chat.py must call as_chat_engine(chat_mode=\"context\") to build the chat engine."
    )
    assert source.count("chat_engine.chat(") >= 2, (
        "chat.py must call chat_engine.chat(...) at least twice (one per turn). "
        f"Found {source.count('chat_engine.chat(')} occurrence(s) in the source."
    )
    assert "chat_engine.reset(" not in source, (
        "chat.py must NOT call chat_engine.reset(...) between turns; "
        "the second turn requires the conversation memory from the first turn."
    )
    assert "/logs/artifacts/trial_id" in source, (
        "chat.py must read the trial_id from /logs/artifacts/trial_id."
    )


def test_script_fails_on_missing_data_dir():
    """The script must exit non-zero when --data-dir does not exist."""
    missing_dir = os.path.join(PROJECT_DIR, "does_not_exist_dir")
    assert not os.path.exists(missing_dir), (
        f"Test prerequisite failed: {missing_dir} should not exist."
    )
    result = subprocess.run(
        [
            "python3",
            "chat.py",
            "--data-dir",
            missing_dir,
            "--message1",
            "anything",
            "--message2",
            "anything else",
            "--output",
            os.path.join(PROJECT_DIR, "should_not_be_written.json"),
        ],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
        timeout=120,
    )
    assert result.returncode != 0, (
        "Expected chat.py to exit with a non-zero status code when "
        f"--data-dir does not exist; got returncode={result.returncode}, "
        f"stdout={result.stdout!r}, stderr={result.stderr!r}"
    )
