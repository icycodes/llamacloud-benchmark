import os
import shutil
import subprocess

PROJECT_DIR = "/home/user/update_task"
INITIAL_DIR = os.path.join(PROJECT_DIR, "data", "initial")
UPDATES_DIR = os.path.join(PROJECT_DIR, "data", "updates")
INITIAL_AURORA = os.path.join(INITIAL_DIR, "atlantis-aurora.txt")
INITIAL_CUISINE = os.path.join(INITIAL_DIR, "atlantis-cuisine.txt")
UPDATED_AURORA = os.path.join(UPDATES_DIR, "atlantis-aurora.txt")


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


def test_initial_data_dir_exists():
    assert os.path.isdir(INITIAL_DIR), (
        f"Seed data directory {INITIAL_DIR} does not exist."
    )


def test_updates_data_dir_exists():
    assert os.path.isdir(UPDATES_DIR), (
        f"Update data directory {UPDATES_DIR} does not exist."
    )


def test_initial_aurora_file_exists_with_expected_content():
    assert os.path.isfile(INITIAL_AURORA), (
        f"Expected pre-seeded {INITIAL_AURORA} was not found."
    )
    with open(INITIAL_AURORA, "r", encoding="utf-8") as fp:
        content = fp.read()
    assert "deep-sea submarine" in content.lower(), (
        f"{INITIAL_AURORA} is missing the expected seeded sentence about the original submarine Aurora."
    )
    assert "sonar-pulse" in content.lower(), (
        f"{INITIAL_AURORA} is missing the expected 'sonar-pulse' phrase from the original Aurora text."
    )


def test_initial_cuisine_file_exists_with_expected_content():
    assert os.path.isfile(INITIAL_CUISINE), (
        f"Expected pre-seeded {INITIAL_CUISINE} was not found."
    )
    with open(INITIAL_CUISINE, "r", encoding="utf-8") as fp:
        content = fp.read()
    assert "grilled seaweed" in content.lower(), (
        f"{INITIAL_CUISINE} is missing the expected seeded sentence about the national dish."
    )


def test_updated_aurora_file_exists_with_expected_content():
    assert os.path.isfile(UPDATED_AURORA), (
        f"Expected pre-seeded {UPDATED_AURORA} was not found."
    )
    with open(UPDATED_AURORA, "r", encoding="utf-8") as fp:
        content = fp.read()
    assert "flying car" in content.lower(), (
        f"{UPDATED_AURORA} is missing the expected corrected 'flying car' phrase."
    )
    assert "anti-gravity" in content.lower(), (
        f"{UPDATED_AURORA} is missing the expected 'anti-gravity' phrase from the corrected Aurora text."
    )


def test_trial_id_file_exists():
    """The harbor trial_id artifact must exist before the task starts."""
    assert os.path.isfile("/logs/artifacts/trial_id"), (
        "/logs/artifacts/trial_id is missing; cannot scope LlamaCloud resources per trial."
    )


def test_update_index_script_not_pre_created():
    """The executor must create update_index.py; it must not exist initially."""
    script_path = os.path.join(PROJECT_DIR, "update_index.py")
    assert not os.path.exists(script_path), (
        f"{script_path} should not exist at task start; the executor must create it."
    )


def test_output_log_not_pre_created():
    """The executor must create output.log; it must not exist initially."""
    output_log = os.path.join(PROJECT_DIR, "output.log")
    assert not os.path.exists(output_log), (
        f"{output_log} should not exist at task start; the executor must create it."
    )
