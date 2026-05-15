import os
import shutil
import subprocess

PROJECT_DIR = "/home/user/myproject"
DOCS_DIR = os.path.join(PROJECT_DIR, "docs")
COMPANY_FILE = os.path.join(DOCS_DIR, "company_profile.txt")


def test_python3_available():
    assert shutil.which("python3") is not None, "python3 binary not found in PATH."


def test_llama_index_managed_package_installed():
    """Verify the llama-index-indices-managed-llama-cloud package is importable."""
    result = subprocess.run(
        [
            "python3",
            "-c",
            "from llama_index.indices.managed.llama_cloud import LlamaCloudIndex; print('ok')",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        "Failed to import LlamaCloudIndex from "
        "llama_index.indices.managed.llama_cloud: "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "ok" in result.stdout, (
        "Expected 'ok' to be printed when importing LlamaCloudIndex, "
        f"got stdout={result.stdout!r}"
    )


def test_llama_index_core_simple_directory_reader_available():
    """Verify that SimpleDirectoryReader from llama_index.core is importable."""
    result = subprocess.run(
        [
            "python3",
            "-c",
            "from llama_index.core import SimpleDirectoryReader; print('ok')",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        "Failed to import SimpleDirectoryReader from llama_index.core: "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "ok" in result.stdout, (
        "Expected 'ok' to be printed when importing SimpleDirectoryReader, "
        f"got stdout={result.stdout!r}"
    )


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_docs_directory_exists():
    assert os.path.isdir(DOCS_DIR), (
        f"Initial docs directory {DOCS_DIR} does not exist."
    )


def test_company_profile_file_exists():
    assert os.path.isfile(COMPANY_FILE), (
        f"Initial sample document {COMPANY_FILE} does not exist."
    )


def test_company_profile_content_present():
    """The initial sample document must mention key facts used by the chat verification."""
    with open(COMPANY_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    assert "Acme Widgets Corporation" in content, (
        "Initial company_profile.txt does not mention 'Acme Widgets Corporation'."
    )
    assert "1957" in content, (
        "Initial company_profile.txt does not mention the founding year 1957."
    )
    assert "Alice Thompson" in content, (
        "Initial company_profile.txt does not mention the CEO 'Alice Thompson'."
    )


def test_trial_id_file_present():
    """The harness must provide /logs/artifacts/trial_id before the task starts."""
    trial_id_path = "/logs/artifacts/trial_id"
    assert os.path.isfile(trial_id_path), (
        f"Expected trial_id file at {trial_id_path}; it is required by the task."
    )
    with open(trial_id_path, "r", encoding="utf-8") as f:
        trial_id = f.read().strip()
    assert trial_id, (
        f"trial_id file {trial_id_path} is empty; the task requires a non-empty trial_id."
    )


def test_llama_cloud_api_key_env_set():
    assert os.environ.get("LLAMA_CLOUD_API_KEY"), (
        "LLAMA_CLOUD_API_KEY environment variable is not set."
    )
