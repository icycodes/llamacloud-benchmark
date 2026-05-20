import json
import os
import subprocess
import sys

import pytest

PROJECT_DIR = "/home/user/myproject"
EXTRACT_SCRIPT = os.path.join(PROJECT_DIR, "extract.py")
SAMPLE_RESUME = os.path.join(PROJECT_DIR, "sample_resume.txt")
RESULT_JSON = os.path.join(PROJECT_DIR, "result.json")
TRIAL_ID_PATH = "/logs/artifacts/trial_id"


def _read_trial_id() -> str:
    with open(TRIAL_ID_PATH, "r", encoding="utf-8") as f:
        return f.read().strip()


def _clean_result_file():
    if os.path.isfile(RESULT_JSON):
        os.remove(RESULT_JSON)


def _run_extract_cli() -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            sys.executable,
            EXTRACT_SCRIPT,
            "--input",
            SAMPLE_RESUME,
            "--output",
            RESULT_JSON,
        ],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
        env=os.environ.copy(),
        timeout=600,
    )


def _validate_result_payload(payload):
    assert isinstance(payload, dict), (
        f"Expected the extracted JSON to be an object, got {type(payload).__name__}."
    )
    assert set(payload.keys()) == {"name", "email", "skills"}, (
        "Expected the extracted JSON to contain exactly the keys "
        f"'name', 'email', 'skills'; got {sorted(payload.keys())}."
    )

    name = payload["name"]
    assert isinstance(name, str) and name.strip(), (
        f"Expected 'name' to be a non-empty string, got {name!r}."
    )
    assert "john smith" in name.lower(), (
        f"Expected the extracted name to contain 'John Smith', got {name!r}."
    )

    email = payload["email"]
    assert isinstance(email, str), (
        f"Expected 'email' to be a string, got {type(email).__name__}."
    )
    assert email.strip().lower() == "john.smith@example.com", (
        "Expected the extracted email to equal 'john.smith@example.com', "
        f"got {email!r}."
    )

    skills = payload["skills"]
    assert isinstance(skills, list) and skills, (
        f"Expected 'skills' to be a non-empty list, got {skills!r}."
    )
    assert all(isinstance(s, str) for s in skills), (
        f"Expected every skill to be a string, got {skills!r}."
    )
    lowered_skills = {s.strip().lower() for s in skills}
    for required in ("python", "go", "kubernetes"):
        assert required in lowered_skills, (
            f"Expected the extracted skills to include '{required}', "
            f"got {skills!r}."
        )


@pytest.fixture(scope="module")
def cli_first_run():
    _clean_result_file()
    result = _run_extract_cli()
    return result


def test_extract_script_exists(cli_first_run):
    assert os.path.isfile(EXTRACT_SCRIPT), (
        f"Expected the extraction CLI at {EXTRACT_SCRIPT}."
    )


def test_cli_runs_successfully(cli_first_run):
    assert cli_first_run.returncode == 0, (
        "Expected the extraction CLI to exit with code 0. "
        f"stdout={cli_first_run.stdout!r}, stderr={cli_first_run.stderr!r}"
    )
    expected_line = f"Extraction completed: {RESULT_JSON}"
    assert expected_line in cli_first_run.stdout, (
        f"Expected stdout to contain {expected_line!r}; "
        f"got stdout={cli_first_run.stdout!r}."
    )


def test_result_json_has_expected_content(cli_first_run):
    assert os.path.isfile(RESULT_JSON), (
        f"Expected the CLI to create {RESULT_JSON}."
    )
    with open(RESULT_JSON, "r", encoding="utf-8") as f:
        payload = json.load(f)
    _validate_result_payload(payload)


def test_extraction_agent_named_with_trial_id(cli_first_run):
    trial_id = _read_trial_id()
    assert trial_id, "Trial id read from /logs/artifacts/trial_id must not be empty."

    from llama_cloud import LlamaCloud

    client = LlamaCloud()
    expected_name = f"resume-parser-{trial_id}"

    agents = list(client.extraction.extraction_agents.list())
    matching = [
        a for a in agents if getattr(a, "name", None) == expected_name
    ]
    assert matching, (
        "Expected to find an extraction agent named "
        f"'{expected_name}' on LlamaCloud, "
        f"got names: {[getattr(a, 'name', None) for a in agents]}."
    )


def test_cli_is_idempotent(cli_first_run):
    # Run again on the same inputs/outputs without cleaning the result first.
    second = _run_extract_cli()
    assert second.returncode == 0, (
        "Expected the extraction CLI to be idempotent and exit with code 0 "
        f"on the second run. stdout={second.stdout!r}, stderr={second.stderr!r}"
    )
    expected_line = f"Extraction completed: {RESULT_JSON}"
    assert expected_line in second.stdout, (
        "Expected stdout on the second run to contain "
        f"{expected_line!r}; got stdout={second.stdout!r}."
    )

    with open(RESULT_JSON, "r", encoding="utf-8") as f:
        payload = json.load(f)
    _validate_result_payload(payload)
