import hashlib
import json
import os
import shutil
import subprocess
import pytest

PROJECT_DIR = "/home/user/incremental_ingest"
DATA_DIR = os.path.join(PROJECT_DIR, "data")
PRIOR_MANIFEST = os.path.join(PROJECT_DIR, "prior_manifest.json")
SYNC_PY = os.path.join(PROJECT_DIR, "sync.py")
CURRENT_MANIFEST = os.path.join(PROJECT_DIR, "current_manifest.json")
UPLOAD_PLAN = os.path.join(PROJECT_DIR, "upload_plan.json")

INTRO_FILE = os.path.join(DATA_DIR, "intro.txt")
GLOSSARY_FILE = os.path.join(DATA_DIR, "glossary.txt")
CHANGELOG_FILE = os.path.join(DATA_DIR, "changelog.txt")


def _sha256_of_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def test_python3_available():
    assert shutil.which("python3") is not None, "python3 binary not found in PATH."


def test_llama_cloud_sdk_installed():
    result = subprocess.run(
        ["python3", "-c", "import llama_cloud; print(llama_cloud.__name__)"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"llama_cloud Python package is not importable. stderr: {result.stderr}"
    )


def test_llama_cloud_client_class_available():
    result = subprocess.run(
        [
            "python3",
            "-c",
            "from llama_cloud import LlamaCloud; print(LlamaCloud.__name__)",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"LlamaCloud client class is not importable from llama_cloud. "
        f"stderr: {result.stderr}"
    )
    assert "LlamaCloud" in result.stdout, (
        f"Expected 'LlamaCloud' to be the class name. stdout: {result.stdout!r}"
    )


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Expected project directory {PROJECT_DIR} to exist before task execution."
    )


def test_data_directory_exists():
    assert os.path.isdir(DATA_DIR), (
        f"Expected data directory {DATA_DIR} to exist before task execution."
    )


def test_intro_file_exists():
    assert os.path.isfile(INTRO_FILE), (
        f"Expected pre-existing file {INTRO_FILE} (unchanged content)."
    )


def test_glossary_file_exists():
    assert os.path.isfile(GLOSSARY_FILE), (
        f"Expected pre-existing file {GLOSSARY_FILE} (modified content)."
    )


def test_changelog_file_exists():
    assert os.path.isfile(CHANGELOG_FILE), (
        f"Expected pre-existing file {CHANGELOG_FILE} (new file not in prior manifest)."
    )


def test_no_removed_doc_file_on_disk():
    removed_doc = os.path.join(DATA_DIR, "removed_doc.txt")
    assert not os.path.exists(removed_doc), (
        f"{removed_doc} must NOT exist on disk — it is only referenced by the prior "
        "manifest so the script can detect it as a deletion."
    )


def test_prior_manifest_exists_and_is_valid_json():
    assert os.path.isfile(PRIOR_MANIFEST), (
        f"Expected {PRIOR_MANIFEST} to exist before task execution."
    )
    with open(PRIOR_MANIFEST, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, dict), (
        f"{PRIOR_MANIFEST} must contain a JSON object. Got: {type(data).__name__}"
    )
    assert "files" in data and isinstance(data["files"], dict), (
        f"{PRIOR_MANIFEST} must contain a 'files' object."
    )


def test_prior_manifest_has_expected_keys():
    with open(PRIOR_MANIFEST, "r", encoding="utf-8") as f:
        data = json.load(f)
    files = data["files"]
    expected_keys = {"intro.txt", "glossary.txt", "removed_doc.txt"}
    assert set(files.keys()) == expected_keys, (
        f"{PRIOR_MANIFEST} 'files' must contain exactly the keys {sorted(expected_keys)}, "
        f"got: {sorted(files.keys())}"
    )


def test_prior_manifest_intro_matches_on_disk():
    """intro.txt should be 'unchanged': the prior manifest sha256 must match the on-disk file."""
    with open(PRIOR_MANIFEST, "r", encoding="utf-8") as f:
        data = json.load(f)
    prior_sha = data["files"]["intro.txt"]["sha256"]
    actual_sha = _sha256_of_file(INTRO_FILE)
    assert prior_sha == actual_sha, (
        f"intro.txt is supposed to be unchanged: prior manifest sha256 {prior_sha!r} "
        f"must equal on-disk sha256 {actual_sha!r}."
    )


def test_prior_manifest_glossary_differs_from_on_disk():
    """glossary.txt should be 'modified': the prior manifest sha256 must NOT match the on-disk file."""
    with open(PRIOR_MANIFEST, "r", encoding="utf-8") as f:
        data = json.load(f)
    prior_sha = data["files"]["glossary.txt"]["sha256"]
    actual_sha = _sha256_of_file(GLOSSARY_FILE)
    assert prior_sha != actual_sha, (
        f"glossary.txt is supposed to be modified: prior manifest sha256 {prior_sha!r} "
        f"must differ from on-disk sha256 {actual_sha!r}."
    )


def test_llama_cloud_api_key_env_set():
    value = os.environ.get("LLAMA_CLOUD_API_KEY")
    assert value is not None and value.strip() != "", (
        "LLAMA_CLOUD_API_KEY environment variable must be set for the task environment."
    )


def test_sync_script_not_yet_created():
    assert not os.path.exists(SYNC_PY), (
        f"Script {SYNC_PY} must not exist before the task is executed."
    )


def test_current_manifest_not_yet_created():
    assert not os.path.exists(CURRENT_MANIFEST), (
        f"Output file {CURRENT_MANIFEST} must not exist before the task is executed."
    )


def test_upload_plan_not_yet_created():
    assert not os.path.exists(UPLOAD_PLAN), (
        f"Output file {UPLOAD_PLAN} must not exist before the task is executed."
    )
