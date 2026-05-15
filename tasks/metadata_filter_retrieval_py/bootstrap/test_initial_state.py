import os
import shutil
import subprocess

PROJECT_DIR = "/home/user/metadata_filter_task"
DATA_DIR = os.path.join(PROJECT_DIR, "data")
FINANCE_FILE = os.path.join(DATA_DIR, "finance", "finance.txt")
SPORTS_FILE = os.path.join(DATA_DIR, "sports", "sports.txt")
GEOGRAPHY_FILE = os.path.join(DATA_DIR, "geography", "geography.txt")


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


def test_metadata_filters_importable():
    """The MetadataFilters primitives must be importable from llama_index.core."""
    result = subprocess.run(
        [
            "python3",
            "-c",
            "from llama_index.core.vector_stores import MetadataFilter, MetadataFilters, FilterOperator",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        "Failed to import MetadataFilter/MetadataFilters/FilterOperator from llama_index.core.vector_stores: "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )


def test_document_importable():
    """The llama_index.core.Document class must be available."""
    result = subprocess.run(
        ["python3", "-c", "from llama_index.core import Document"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Failed to import Document from llama_index.core: "
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


def test_finance_file_exists_with_expected_content():
    assert os.path.isfile(FINANCE_FILE), (
        f"Expected pre-seeded {FINANCE_FILE} was not found."
    )
    with open(FINANCE_FILE, "r", encoding="utf-8") as fp:
        content = fp.read()
    assert "Globex Industries" in content, (
        f"{FINANCE_FILE} is missing the expected seeded sentence about Globex Industries."
    )


def test_sports_file_exists_with_expected_content():
    assert os.path.isfile(SPORTS_FILE), (
        f"Expected pre-seeded {SPORTS_FILE} was not found."
    )
    with open(SPORTS_FILE, "r", encoding="utf-8") as fp:
        content = fp.read()
    assert "Atlas Kim" in content, (
        f"{SPORTS_FILE} is missing the expected seeded sentence about Atlas Kim."
    )


def test_geography_file_exists_with_expected_content():
    assert os.path.isfile(GEOGRAPHY_FILE), (
        f"Expected pre-seeded {GEOGRAPHY_FILE} was not found."
    )
    with open(GEOGRAPHY_FILE, "r", encoding="utf-8") as fp:
        content = fp.read()
    assert "Mount Aurelius" in content, (
        f"{GEOGRAPHY_FILE} is missing the expected seeded sentence about Mount Aurelius."
    )


def test_trial_id_file_exists():
    """The harbor trial_id artifact must exist before the task starts."""
    assert os.path.isfile("/logs/artifacts/trial_id"), (
        "/logs/artifacts/trial_id is missing; cannot scope LlamaCloud resources per trial."
    )


def test_script_not_pre_created():
    """The executor must create filter_retrieve.py; it must not exist initially."""
    script = os.path.join(PROJECT_DIR, "filter_retrieve.py")
    assert not os.path.exists(script), (
        f"{script} should not exist at task start; the executor must create it."
    )


def test_output_log_not_pre_created():
    """The executor must create output.log; it must not exist initially."""
    output_log = os.path.join(PROJECT_DIR, "output.log")
    assert not os.path.exists(output_log), (
        f"{output_log} should not exist at task start; the executor must create it."
    )
