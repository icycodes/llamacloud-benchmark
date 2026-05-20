import os
import shutil
import subprocess

PROJECT_DIR = "/home/user/delete_task"
DATA_DIR = os.path.join(PROJECT_DIR, "data")
HISTORY_FILE = os.path.join(DATA_DIR, "history.txt")
CUISINE_FILE = os.path.join(DATA_DIR, "cuisine.txt")
SECRET_FILE = os.path.join(DATA_DIR, "secret.txt")


def test_python3_available():
    assert shutil.which("python3") is not None, "python3 binary not found in PATH."


def test_llama_cloud_managed_index_importable():
    """The LlamaCloud managed-index integration must already be installed."""
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
        "Failed to import LlamaCloudIndex from llama_index.indices.managed.llama_cloud: "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )


def test_llama_cloud_sdk_importable():
    """The standalone LlamaCloud SDK must also be installed for verification use."""
    result = subprocess.run(
        ["python3", "-c", "import llama_cloud"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Failed to import llama_cloud: stdout={result.stdout!r} stderr={result.stderr!r}"
    )


def test_document_class_importable():
    """The base Document class must be available from llama_index.core for explicit-id construction."""
    result = subprocess.run(
        ["python3", "-c", "from llama_index.core import Document"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        "Failed to import Document from llama_index.core: "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_data_dir_exists():
    assert os.path.isdir(DATA_DIR), (
        f"Seed data directory {DATA_DIR} does not exist."
    )


def test_history_file_exists_with_expected_content():
    assert os.path.isfile(HISTORY_FILE), (
        f"Expected pre-seeded {HISTORY_FILE} was not found."
    )
    with open(HISTORY_FILE, "r", encoding="utf-8") as fp:
        content = fp.read()
    assert "Atlantis was founded in the year 1042" in content, (
        f"{HISTORY_FILE} is missing the expected seeded sentence about Atlantis history."
    )


def test_cuisine_file_exists_with_expected_content():
    assert os.path.isfile(CUISINE_FILE), (
        f"Expected pre-seeded {CUISINE_FILE} was not found."
    )
    with open(CUISINE_FILE, "r", encoding="utf-8") as fp:
        content = fp.read()
    assert "grilled seaweed" in content.lower(), (
        f"{CUISINE_FILE} is missing the expected seeded sentence about the national dish."
    )


def test_secret_file_exists_with_expected_content():
    assert os.path.isfile(SECRET_FILE), (
        f"Expected pre-seeded {SECRET_FILE} was not found."
    )
    with open(SECRET_FILE, "r", encoding="utf-8") as fp:
        content = fp.read()
    assert "lumina sphere" in content.lower(), (
        f"{SECRET_FILE} is missing the expected seeded sentence about the Lumina Sphere."
    )


def test_trial_id_file_exists():
    """The harbor trial_id artifact must exist before the task starts."""
    assert os.path.isfile("/logs/artifacts/trial_id"), (
        "/logs/artifacts/trial_id is missing; cannot scope LlamaCloud resources per trial."
    )


def test_manage_index_script_not_pre_created():
    """The executor must create manage_index.py; it must not exist initially."""
    script_path = os.path.join(PROJECT_DIR, "manage_index.py")
    assert not os.path.exists(script_path), (
        f"{script_path} should not exist at task start; the executor must create it."
    )


def test_output_log_not_pre_created():
    """The executor must create output.log; it must not exist initially."""
    output_log = os.path.join(PROJECT_DIR, "output.log")
    assert not os.path.exists(output_log), (
        f"{output_log} should not exist at task start; the executor must create it."
    )
