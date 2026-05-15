import os
import shutil
import subprocess
import pytest

PROJECT_DIR = "/home/user/myproject"
INITIAL_DIR = os.path.join(PROJECT_DIR, "initial_docs")
NEW_DIR = os.path.join(PROJECT_DIR, "new_docs")
TRIAL_ID_FILE = "/logs/artifacts/trial_id"


def test_python3_binary_available():
    assert shutil.which("python3") is not None, \
        "python3 binary not found in PATH."


def test_pip3_binary_available():
    assert shutil.which("pip3") is not None, \
        "pip3 binary not found in PATH."


def test_llama_index_managed_llama_cloud_installed():
    """The target library (managed LlamaCloud integration) must be importable."""
    result = subprocess.run(
        [
            "python3",
            "-c",
            "from llama_index.indices.managed.llama_cloud import LlamaCloudIndex",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        "Expected `from llama_index.indices.managed.llama_cloud import LlamaCloudIndex` "
        f"to succeed, but it failed with: {result.stderr}"
    )


def test_llama_index_core_simple_directory_reader_installed():
    """`llama_index.core.SimpleDirectoryReader` must be importable."""
    result = subprocess.run(
        [
            "python3",
            "-c",
            "from llama_index.core import SimpleDirectoryReader",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        "Expected `from llama_index.core import SimpleDirectoryReader` to succeed, "
        f"but it failed with: {result.stderr}"
    )


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), \
        f"Project directory {PROJECT_DIR} does not exist."


def test_initial_docs_directory_exists():
    assert os.path.isdir(INITIAL_DIR), \
        f"Initial docs directory {INITIAL_DIR} does not exist."


def test_initial_docs_company_overview_present():
    p = os.path.join(INITIAL_DIR, "company_overview.txt")
    assert os.path.isfile(p), \
        f"Expected initial document {p} to exist before the task starts."
    with open(p, "r", encoding="utf-8") as f:
        content = f.read()
    assert "Acme Widgets Corporation" in content, (
        f"Expected initial document {p} to contain 'Acme Widgets Corporation'."
    )
    assert "1957" in content, (
        f"Expected initial document {p} to mention the founding year 1957."
    )


def test_new_docs_directory_exists():
    assert os.path.isdir(NEW_DIR), \
        f"New docs directory {NEW_DIR} does not exist."


def test_new_docs_leadership_present():
    p = os.path.join(NEW_DIR, "leadership.txt")
    assert os.path.isfile(p), \
        f"Expected new document {p} to exist before the task starts."
    with open(p, "r", encoding="utf-8") as f:
        content = f.read()
    assert "Alice Thompson" in content, (
        f"Expected new document {p} to contain 'Alice Thompson'."
    )


def test_new_docs_headcount_present():
    p = os.path.join(NEW_DIR, "headcount.txt")
    assert os.path.isfile(p), \
        f"Expected new document {p} to exist before the task starts."
    with open(p, "r", encoding="utf-8") as f:
        content = f.read()
    assert "5,234" in content, (
        f"Expected new document {p} to contain the headcount '5,234'."
    )


def test_llama_cloud_api_key_env_var_set():
    assert os.environ.get("LLAMA_CLOUD_API_KEY"), \
        "LLAMA_CLOUD_API_KEY environment variable is not set."


def test_trial_id_file_exists():
    assert os.path.isfile(TRIAL_ID_FILE), \
        f"Expected trial id file {TRIAL_ID_FILE} to exist."
    with open(TRIAL_ID_FILE, "r", encoding="utf-8") as f:
        trial_id = f.read().strip()
    assert trial_id, f"Expected non-empty trial id at {TRIAL_ID_FILE}."
