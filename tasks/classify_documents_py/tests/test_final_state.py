import json
import os
import re
import subprocess

import pytest

PROJECT_DIR = "/home/user/myproject"
SCRIPT_PATH = os.path.join(PROJECT_DIR, "classify_docs.py")
DOCS_DIR = os.path.join(PROJECT_DIR, "docs")
OUTPUT_JSON = os.path.join(PROJECT_DIR, "output.json")
OUTPUT_LOG = os.path.join(PROJECT_DIR, "output.log")
TRIAL_ID_PATH = "/logs/artifacts/trial_id"

EXPECTED_CLASSIFICATIONS = {
    "invoice.pdf": "invoice",
    "receipt.pdf": "receipt",
    "contract.pdf": "contract",
}


def _read_trial_id() -> str:
    with open(TRIAL_ID_PATH, "r", encoding="utf-8") as f:
        return f.read().strip()


@pytest.fixture(scope="session", autouse=True)
def run_agent_script():
    """Clean previously generated outputs and execute the agent's script once."""
    assert os.path.isfile(SCRIPT_PATH), (
        f"Agent's script {SCRIPT_PATH} does not exist. The agent must create it."
    )
    assert os.path.isdir(DOCS_DIR), (
        f"Required docs directory {DOCS_DIR} is missing."
    )
    for filename in EXPECTED_CLASSIFICATIONS:
        fixture_path = os.path.join(DOCS_DIR, filename)
        assert os.path.isfile(fixture_path), (
            f"Required fixture file {fixture_path} is missing."
        )

    for path in (OUTPUT_JSON, OUTPUT_LOG):
        if os.path.isfile(path):
            os.remove(path)

    completed = subprocess.run(
        ["python3", SCRIPT_PATH],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=900,
    )
    yield completed


def test_script_exit_code_is_zero(run_agent_script):
    """The agent's classify_docs.py must run to completion with exit code 0."""
    completed = run_agent_script
    assert completed.returncode == 0, (
        f"classify_docs.py exited with non-zero status {completed.returncode}.\n"
        f"STDOUT:\n{completed.stdout}\n"
        f"STDERR:\n{completed.stderr}"
    )


def test_output_json_file_exists():
    """The classification JSON output file must exist and be non-empty."""
    assert os.path.isfile(OUTPUT_JSON), (
        f"Expected JSON output file at {OUTPUT_JSON} to be created by the script."
    )
    assert os.path.getsize(OUTPUT_JSON) > 0, (
        f"JSON output file {OUTPUT_JSON} exists but is empty."
    )


def _load_output_json():
    with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def test_output_json_top_level_shape():
    """The JSON output must be a dict with the required top-level keys."""
    data = _load_output_json()
    assert isinstance(data, dict), (
        f"{OUTPUT_JSON} must contain a JSON object at the top level, got "
        f"{type(data).__name__}."
    )
    for key in ("trial_id", "total_files", "results"):
        assert key in data, (
            f"Expected top-level key `{key}` in {OUTPUT_JSON}, but it is missing.\n"
            f"Keys present: {sorted(data.keys())}"
        )


def test_output_json_trial_id_matches():
    """`output.json['trial_id']` must equal the harness trial_id."""
    data = _load_output_json()
    expected = _read_trial_id()
    assert data.get("trial_id") == expected, (
        f"Expected `trial_id` in {OUTPUT_JSON} to equal `{expected}` (from "
        f"{TRIAL_ID_PATH}), got `{data.get('trial_id')!r}`."
    )


def test_output_json_total_files_is_valid_integer():
    """`output.json['total_files']` must be an integer >= 3."""
    data = _load_output_json()
    total_files = data.get("total_files")
    assert isinstance(total_files, int) and not isinstance(total_files, bool), (
        f"Expected `total_files` in {OUTPUT_JSON} to be an integer, got "
        f"{type(total_files).__name__} ({total_files!r})."
    )
    assert total_files >= 3, (
        f"Expected `total_files` in {OUTPUT_JSON} to be >= 3, got {total_files}."
    )


def test_output_json_results_structure():
    """Every entry in `results` must include the required keys with correct types."""
    data = _load_output_json()
    results = data.get("results")
    assert isinstance(results, list), (
        f"Expected `results` in {OUTPUT_JSON} to be a list, got "
        f"{type(results).__name__}."
    )
    total_files = data.get("total_files")
    assert len(results) == total_files, (
        f"Expected `len(results) == total_files`, but len(results)={len(results)} "
        f"and total_files={total_files}."
    )
    for idx, entry in enumerate(results):
        assert isinstance(entry, dict), (
            f"results[{idx}] must be a dict, got {type(entry).__name__}."
        )
        for key in ("file_name", "type", "confidence", "reasoning"):
            assert key in entry, (
                f"results[{idx}] missing required key `{key}`. "
                f"Keys present: {sorted(entry.keys())}"
            )
        file_name = entry["file_name"]
        assert isinstance(file_name, str) and file_name.lower().endswith(".pdf"), (
            f"results[{idx}].file_name must be a string ending in `.pdf`, "
            f"got {file_name!r}."
        )
        confidence = entry["confidence"]
        assert isinstance(confidence, (int, float)) and not isinstance(
            confidence, bool
        ), (
            f"results[{idx}].confidence must be a number, got "
            f"{type(confidence).__name__} ({confidence!r})."
        )
        reasoning = entry["reasoning"]
        assert isinstance(reasoning, str) and reasoning.strip(), (
            f"results[{idx}].reasoning must be a non-empty string, got "
            f"{reasoning!r}."
        )


def _find_result_for(file_name: str) -> dict:
    data = _load_output_json()
    matches = [
        entry
        for entry in data.get("results", [])
        if os.path.basename(str(entry.get("file_name", ""))).lower()
        == file_name.lower()
    ]
    assert len(matches) == 1, (
        f"Expected exactly one entry in {OUTPUT_JSON} with file_name=={file_name!r}, "
        f"found {len(matches)}."
    )
    return matches[0]


@pytest.mark.parametrize(
    "file_name,expected_type",
    sorted(EXPECTED_CLASSIFICATIONS.items()),
)
def test_output_json_per_file_classification(file_name, expected_type):
    """Each fixture PDF must be classified with the expected label."""
    entry = _find_result_for(file_name)
    actual_type = str(entry.get("type", "")).strip().lower()
    assert actual_type == expected_type.lower(), (
        f"Expected {file_name} to be classified as `{expected_type}`, "
        f"got `{entry.get('type')!r}` in {OUTPUT_JSON}."
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
    """The log file must contain a `trial_id: <value>` line matching the harness value."""
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


def test_output_log_contains_total_files_line():
    """The log file must contain a `total_files: <N>` line with N >= 3."""
    with open(OUTPUT_LOG, "r", encoding="utf-8") as f:
        log_content = f.read()
    match = re.search(
        r"^\s*total_files\s*:\s*(\d+)\s*$",
        log_content,
        re.MULTILINE,
    )
    assert match, (
        f"Expected {OUTPUT_LOG} to contain a line matching `total_files: <N>`, "
        f"but no such line was found.\nLog content:\n{log_content!r}"
    )
    num = int(match.group(1))
    assert num >= 3, f"Expected total_files in log to be >= 3, got {num}."


@pytest.mark.parametrize(
    "file_name,expected_type",
    sorted(EXPECTED_CLASSIFICATIONS.items()),
)
def test_output_log_contains_per_file_classification(file_name, expected_type):
    """The log file must contain a `<file_name>: <type>` line for every fixture PDF."""
    with open(OUTPUT_LOG, "r", encoding="utf-8") as f:
        log_content = f.read()
    pattern = re.compile(
        r"^\s*"
        + re.escape(file_name)
        + r"\s*:\s*"
        + re.escape(expected_type)
        + r"\s*$",
        re.MULTILINE | re.IGNORECASE,
    )
    assert pattern.search(log_content), (
        f"Expected {OUTPUT_LOG} to contain a line `{file_name}: {expected_type}` "
        f"(case-insensitive on the type value), but no such line was found.\n"
        f"Log content:\n{log_content!r}"
    )
