import hashlib
import json
import os
import subprocess

import pytest

PROJECT_DIR = "/home/user/parse_planner"
INPUTS_DIR = os.path.join(PROJECT_DIR, "inputs")
SCRIPT_PATH = os.path.join(PROJECT_DIR, "parse_plan.py")
PLAN_PATH = os.path.join(PROJECT_DIR, "plan.json")
MISSING_PLAN_PATH = os.path.join(PROJECT_DIR, "should_not_exist.json")
MISSING_DIR = os.path.join(PROJECT_DIR, "does_not_exist")

DATA_TXT = os.path.join(INPUTS_DIR, "data.txt")
NOTES_MD = os.path.join(INPUTS_DIR, "notes.md")


def _sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


@pytest.fixture(scope="module", autouse=True)
def cleanup_and_run_happy_path():
    """Clean stale artifacts and execute the happy-path command before tests."""
    # Cleanup before running
    for stale in (PLAN_PATH, MISSING_PLAN_PATH):
        if os.path.exists(stale):
            os.remove(stale)

    yield

    # No explicit teardown required.


def test_script_file_exists():
    assert os.path.isfile(SCRIPT_PATH), (
        f"Expected user script at {SCRIPT_PATH} but it does not exist."
    )


def test_script_imports_llamaparse_from_llama_cloud_services():
    with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
        source = f.read()
    assert "from llama_cloud_services import LlamaParse" in source, (
        "parse_plan.py must contain the exact import "
        "'from llama_cloud_services import LlamaParse'."
    )
    assert "LlamaParse(" in source, (
        "parse_plan.py must instantiate LlamaParse via 'LlamaParse(' call."
    )


def test_happy_path_run_succeeds():
    """Run the happy-path command and verify exit code and stdout."""
    if os.path.exists(PLAN_PATH):
        os.remove(PLAN_PATH)
    result = subprocess.run(
        [
            "python3",
            SCRIPT_PATH,
            "--input-dir",
            INPUTS_DIR,
            "--output",
            PLAN_PATH,
            "--result-type",
            "markdown",
            "--num-workers",
            "3",
            "--language",
            "en",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Happy-path command failed with exit code {result.returncode}. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    expected_line = (
        f"Parse plan created with 2 files at {PLAN_PATH}"
    )
    stdout_lines = [line for line in result.stdout.splitlines() if line.strip()]
    assert expected_line in stdout_lines, (
        f"Expected stdout to contain exactly the line {expected_line!r}, "
        f"got: {result.stdout!r}"
    )


def test_plan_file_top_level_schema():
    assert os.path.isfile(PLAN_PATH), (
        f"Plan file {PLAN_PATH} was not created by the happy-path run."
    )
    with open(PLAN_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert set(data.keys()) == {"parser_config", "files"}, (
        f"Plan JSON top-level keys must be exactly 'parser_config' and 'files', "
        f"got: {sorted(data.keys())}"
    )
    assert data["parser_config"] == {
        "result_type": "markdown",
        "num_workers": 3,
        "language": "en",
    }, (
        f"parser_config does not match expected values; got: {data['parser_config']!r}"
    )
    assert isinstance(data["files"], list) and len(data["files"]) == 2, (
        f"Expected exactly 2 file entries in 'files', got: {data['files']!r}"
    )


def test_plan_file_data_txt_entry():
    with open(PLAN_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    entry = data["files"][0]
    assert entry["file_name"] == "data.txt", (
        f"Expected files[0].file_name == 'data.txt' (alphabetical), "
        f"got: {entry['file_name']!r}"
    )
    assert entry["path"] == DATA_TXT, (
        f"Expected files[0].path == {DATA_TXT!r}, got: {entry['path']!r}"
    )
    expected_size = os.path.getsize(DATA_TXT)
    assert entry["size_bytes"] == expected_size, (
        f"Expected files[0].size_bytes == {expected_size}, "
        f"got: {entry['size_bytes']!r}"
    )
    expected_sha = _sha256_of(DATA_TXT)
    assert entry["sha256"] == expected_sha, (
        f"Expected files[0].sha256 == {expected_sha!r}, got: {entry['sha256']!r}"
    )
    assert entry["extra_info"] == {"file_name": "data.txt"}, (
        f"Expected files[0].extra_info == {{'file_name': 'data.txt'}}, "
        f"got: {entry['extra_info']!r}"
    )


def test_plan_file_notes_md_entry():
    with open(PLAN_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    entry = data["files"][1]
    assert entry["file_name"] == "notes.md", (
        f"Expected files[1].file_name == 'notes.md' (alphabetical), "
        f"got: {entry['file_name']!r}"
    )
    assert entry["path"] == NOTES_MD, (
        f"Expected files[1].path == {NOTES_MD!r}, got: {entry['path']!r}"
    )
    expected_size = os.path.getsize(NOTES_MD)
    assert entry["size_bytes"] == expected_size, (
        f"Expected files[1].size_bytes == {expected_size}, "
        f"got: {entry['size_bytes']!r}"
    )
    expected_sha = _sha256_of(NOTES_MD)
    assert entry["sha256"] == expected_sha, (
        f"Expected files[1].sha256 == {expected_sha!r}, got: {entry['sha256']!r}"
    )
    assert entry["extra_info"] == {"file_name": "notes.md"}, (
        f"Expected files[1].extra_info == {{'file_name': 'notes.md'}}, "
        f"got: {entry['extra_info']!r}"
    )


def test_unsupported_image_jpg_excluded():
    with open(PLAN_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    names = [entry["file_name"] for entry in data["files"]]
    assert "image.jpg" not in names, (
        f"Unsupported file 'image.jpg' must be excluded from the plan, "
        f"but it appeared in: {names!r}"
    )


def test_error_path_missing_input_dir():
    """Run with a non-existent input directory and verify error behaviour."""
    if os.path.exists(MISSING_PLAN_PATH):
        os.remove(MISSING_PLAN_PATH)
    result = subprocess.run(
        [
            "python3",
            SCRIPT_PATH,
            "--input-dir",
            MISSING_DIR,
            "--output",
            MISSING_PLAN_PATH,
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0, (
        f"Expected non-zero exit code when input dir is missing, "
        f"got: {result.returncode}. stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    expected_err = f"Error: input directory not found: {MISSING_DIR}"
    assert expected_err in result.stderr, (
        f"Expected stderr to contain {expected_err!r}, got: {result.stderr!r}"
    )
    assert not os.path.exists(MISSING_PLAN_PATH), (
        f"Output file {MISSING_PLAN_PATH} must NOT be created on the error path."
    )
