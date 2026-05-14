import hashlib
import json
import os
import subprocess

import pytest

PROJECT_DIR = "/home/user/sync_planner"
INPUTS_DIR = os.path.join(PROJECT_DIR, "inputs")
REPORT_MD = os.path.join(INPUTS_DIR, "report.md")
NOTES_TXT = os.path.join(INPUTS_DIR, "notes.txt")
SCRIPT_PATH = os.path.join(PROJECT_DIR, "sync_planner.py")
PREVIOUS_STATE = os.path.join(PROJECT_DIR, "previous_state.json")
PLAN_PATH = os.path.join(PROJECT_DIR, "plan.json")
INITIAL_PLAN_PATH = os.path.join(PROJECT_DIR, "initial_plan.json")
NO_SUCH_STATE = os.path.join(PROJECT_DIR, "no_such_state.json")
SHOULD_NOT_EXIST = os.path.join(PROJECT_DIR, "should_not_exist.json")
MISSING_INPUT_DIR = os.path.join(PROJECT_DIR, "does_not_exist")

ZERO_SHA = "0000000000000000000000000000000000000000000000000000000000000000"


def _sha256_of_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


@pytest.fixture(autouse=True)
def cleanup_generated_files():
    """Remove any artifacts a previous test run may have produced so each test starts clean."""
    for path in (PLAN_PATH, INITIAL_PLAN_PATH, SHOULD_NOT_EXIST, NO_SUCH_STATE):
        if os.path.exists(path):
            os.remove(path)
    yield


def test_script_imports_llama_cloud_managed_index():
    """The submitted script must import LlamaCloudIndex from the managed-index SDK."""
    assert os.path.isfile(SCRIPT_PATH), (
        f"Expected the agent to create the script at {SCRIPT_PATH}, but it is missing."
    )
    with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
        source = f.read()
    assert (
        "from llama_index.indices.managed.llama_cloud import LlamaCloudIndex"
        in source
    ), (
        "sync_planner.py must contain the literal import "
        "'from llama_index.indices.managed.llama_cloud import LlamaCloudIndex' "
        "to demonstrate correct SDK wiring."
    )


def test_happy_path_run_stdout_and_exit_code():
    """Run the script with the baseline previous_state.json and verify stdout + exit code."""
    result = subprocess.run(
        [
            "python3",
            SCRIPT_PATH,
            "--input-dir",
            INPUTS_DIR,
            "--previous-state",
            PREVIOUS_STATE,
            "--output",
            PLAN_PATH,
            "--index-name",
            "my_index",
            "--project-name",
            "Default",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Expected exit code 0, got {result.returncode}. stderr: {result.stderr}"
    )
    expected_line = (
        f"Sync plan written to {PLAN_PATH}: add=1 update=0 unchanged=1 delete=1"
    )
    assert result.stdout.strip() == expected_line, (
        f"Expected stdout to be exactly:\n{expected_line!r}\nGot:\n{result.stdout!r}"
    )


def test_happy_path_plan_structure():
    """Happy-path plan must have the documented top-level keys and summary counts."""
    subprocess.run(
        [
            "python3",
            SCRIPT_PATH,
            "--input-dir",
            INPUTS_DIR,
            "--previous-state",
            PREVIOUS_STATE,
            "--output",
            PLAN_PATH,
            "--index-name",
            "my_index",
            "--project-name",
            "Default",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert os.path.isfile(PLAN_PATH), f"Plan file {PLAN_PATH} was not created."
    with open(PLAN_PATH, "r", encoding="utf-8") as f:
        plan = json.load(f)
    assert set(plan.keys()) == {"index_name", "project_name", "actions", "summary"}, (
        f"Plan top-level keys must be exactly index_name, project_name, actions, summary; got {sorted(plan.keys())}."
    )
    assert plan["index_name"] == "my_index", (
        f"index_name should be 'my_index', got {plan['index_name']!r}."
    )
    assert plan["project_name"] == "Default", (
        f"project_name should be 'Default', got {plan['project_name']!r}."
    )
    assert set(plan["actions"].keys()) == {"add", "update", "unchanged", "delete"}, (
        f"actions keys must be exactly add, update, unchanged, delete; got {sorted(plan['actions'].keys())}."
    )
    assert plan["summary"] == {"add": 1, "update": 0, "unchanged": 1, "delete": 1}, (
        f"summary should be add=1 update=0 unchanged=1 delete=1; got {plan['summary']!r}."
    )
    for action_name in ("add", "update", "unchanged", "delete"):
        assert plan["summary"][action_name] == len(plan["actions"][action_name]), (
            f"summary.{action_name}={plan['summary'][action_name]} must equal "
            f"len(actions.{action_name})={len(plan['actions'][action_name])}."
        )


def test_happy_path_add_entry_for_notes_txt():
    """notes.txt is new on disk and must appear in actions.add with correct metadata."""
    subprocess.run(
        [
            "python3",
            SCRIPT_PATH,
            "--input-dir",
            INPUTS_DIR,
            "--previous-state",
            PREVIOUS_STATE,
            "--output",
            PLAN_PATH,
            "--index-name",
            "my_index",
            "--project-name",
            "Default",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    with open(PLAN_PATH, "r", encoding="utf-8") as f:
        plan = json.load(f)
    add_list = plan["actions"]["add"]
    assert len(add_list) == 1, (
        f"Expected exactly one ADD entry (for notes.txt); got {len(add_list)}: {add_list!r}."
    )
    entry = add_list[0]
    assert entry["file_name"] == "notes.txt", (
        f"ADD entry file_name must be 'notes.txt'; got {entry.get('file_name')!r}."
    )
    assert entry["path"] == NOTES_TXT, (
        f"ADD entry path must be {NOTES_TXT}; got {entry.get('path')!r}."
    )
    assert entry["size_bytes"] == os.path.getsize(NOTES_TXT), (
        f"ADD entry size_bytes must equal on-disk size {os.path.getsize(NOTES_TXT)}; got {entry.get('size_bytes')!r}."
    )
    assert entry["sha256"] == _sha256_of_file(NOTES_TXT), (
        "ADD entry sha256 must equal the lowercase hex SHA-256 of the on-disk notes.txt."
    )


def test_happy_path_unchanged_entry_for_report_md():
    """report.md is in both baseline and disk with the same hash -> must be UNCHANGED."""
    subprocess.run(
        [
            "python3",
            SCRIPT_PATH,
            "--input-dir",
            INPUTS_DIR,
            "--previous-state",
            PREVIOUS_STATE,
            "--output",
            PLAN_PATH,
            "--index-name",
            "my_index",
            "--project-name",
            "Default",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    with open(PLAN_PATH, "r", encoding="utf-8") as f:
        plan = json.load(f)
    unchanged_list = plan["actions"]["unchanged"]
    assert len(unchanged_list) == 1, (
        f"Expected exactly one UNCHANGED entry (for report.md); got {len(unchanged_list)}: {unchanged_list!r}."
    )
    entry = unchanged_list[0]
    assert entry["file_name"] == "report.md", (
        f"UNCHANGED entry file_name must be 'report.md'; got {entry.get('file_name')!r}."
    )
    assert entry["sha256"] == _sha256_of_file(REPORT_MD), (
        "UNCHANGED entry sha256 must equal the lowercase hex SHA-256 of the on-disk report.md."
    )


def test_happy_path_delete_entry_for_archive_txt():
    """archive.txt was in baseline but not on disk -> must be DELETE."""
    subprocess.run(
        [
            "python3",
            SCRIPT_PATH,
            "--input-dir",
            INPUTS_DIR,
            "--previous-state",
            PREVIOUS_STATE,
            "--output",
            PLAN_PATH,
            "--index-name",
            "my_index",
            "--project-name",
            "Default",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    with open(PLAN_PATH, "r", encoding="utf-8") as f:
        plan = json.load(f)
    delete_list = plan["actions"]["delete"]
    assert len(delete_list) == 1, (
        f"Expected exactly one DELETE entry (for archive.txt); got {len(delete_list)}: {delete_list!r}."
    )
    entry = delete_list[0]
    assert entry["file_name"] == "archive.txt", (
        f"DELETE entry file_name must be 'archive.txt'; got {entry.get('file_name')!r}."
    )
    assert entry["previous_sha256"] == ZERO_SHA, (
        f"DELETE entry previous_sha256 must equal the baseline value {ZERO_SHA!r}; got {entry.get('previous_sha256')!r}."
    )


def test_happy_path_update_list_empty_and_unsupported_excluded():
    """No file should match UPDATE in the happy path, and image.jpg must be ignored."""
    subprocess.run(
        [
            "python3",
            SCRIPT_PATH,
            "--input-dir",
            INPUTS_DIR,
            "--previous-state",
            PREVIOUS_STATE,
            "--output",
            PLAN_PATH,
            "--index-name",
            "my_index",
            "--project-name",
            "Default",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    with open(PLAN_PATH, "r", encoding="utf-8") as f:
        plan = json.load(f)
    assert plan["actions"]["update"] == [], (
        f"Expected actions.update to be empty in the happy path; got {plan['actions']['update']!r}."
    )
    all_names = set()
    for action_name in ("add", "update", "unchanged", "delete"):
        for entry in plan["actions"][action_name]:
            all_names.add(entry.get("file_name"))
    assert "image.jpg" not in all_names, (
        f"image.jpg must never appear in any action list (unsupported extension); got names: {sorted(all_names)!r}."
    )


def test_missing_previous_state_run():
    """When --previous-state points at a missing file, every current file becomes ADD."""
    result = subprocess.run(
        [
            "python3",
            SCRIPT_PATH,
            "--input-dir",
            INPUTS_DIR,
            "--previous-state",
            NO_SUCH_STATE,
            "--output",
            INITIAL_PLAN_PATH,
            "--index-name",
            "my_index",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Expected exit code 0 when --previous-state is missing; got {result.returncode}. stderr: {result.stderr}"
    )
    expected_line = (
        f"Sync plan written to {INITIAL_PLAN_PATH}: add=2 update=0 unchanged=0 delete=0"
    )
    assert result.stdout.strip() == expected_line, (
        f"Expected stdout to be exactly:\n{expected_line!r}\nGot:\n{result.stdout!r}"
    )
    assert os.path.isfile(INITIAL_PLAN_PATH), (
        f"Plan file {INITIAL_PLAN_PATH} was not created."
    )
    with open(INITIAL_PLAN_PATH, "r", encoding="utf-8") as f:
        plan = json.load(f)
    assert plan["project_name"] == "Default", (
        f"project_name must default to 'Default' when --project-name is omitted; got {plan['project_name']!r}."
    )
    assert plan["actions"]["update"] == [], (
        f"Expected actions.update to be empty; got {plan['actions']['update']!r}."
    )
    assert plan["actions"]["unchanged"] == [], (
        f"Expected actions.unchanged to be empty; got {plan['actions']['unchanged']!r}."
    )
    assert plan["actions"]["delete"] == [], (
        f"Expected actions.delete to be empty; got {plan['actions']['delete']!r}."
    )
    add_list = plan["actions"]["add"]
    assert len(add_list) == 2, (
        f"Expected actions.add to contain 2 entries (notes.txt and report.md); got {len(add_list)}: {add_list!r}."
    )
    assert add_list[0]["file_name"] == "notes.txt", (
        f"actions.add[0].file_name must be 'notes.txt' (alphabetical order); got {add_list[0].get('file_name')!r}."
    )
    assert add_list[1]["file_name"] == "report.md", (
        f"actions.add[1].file_name must be 'report.md' (alphabetical order); got {add_list[1].get('file_name')!r}."
    )
    assert plan["summary"] == {"add": 2, "update": 0, "unchanged": 0, "delete": 0}, (
        f"summary should be add=2 update=0 unchanged=0 delete=0; got {plan['summary']!r}."
    )


def test_missing_input_directory_error_path():
    """When --input-dir does not exist, the script must error to stderr and not create the output."""
    result = subprocess.run(
        [
            "python3",
            SCRIPT_PATH,
            "--input-dir",
            MISSING_INPUT_DIR,
            "--previous-state",
            PREVIOUS_STATE,
            "--output",
            SHOULD_NOT_EXIST,
            "--index-name",
            "my_index",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0, (
        f"Expected a non-zero exit code when --input-dir is missing; got {result.returncode}. stdout: {result.stdout}"
    )
    expected_err_line = f"Error: input directory not found: {MISSING_INPUT_DIR}"
    assert expected_err_line in result.stderr, (
        f"Expected stderr to contain:\n{expected_err_line!r}\nGot stderr:\n{result.stderr!r}"
    )
    assert not os.path.exists(SHOULD_NOT_EXIST), (
        f"{SHOULD_NOT_EXIST} must NOT be created when the input directory is missing."
    )
