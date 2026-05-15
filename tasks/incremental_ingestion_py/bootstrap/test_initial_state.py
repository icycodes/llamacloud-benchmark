import os
import shutil
import subprocess

PROJECT_DIR = "/home/user/ingest_task"
INITIAL_DATA_DIR = os.path.join(PROJECT_DIR, "initial_data")
EXTRA_DATA_DIR = os.path.join(PROJECT_DIR, "extra_data")

ANIMALS_FILE = os.path.join(INITIAL_DATA_DIR, "animals.txt")
GEOGRAPHY_FILE = os.path.join(INITIAL_DATA_DIR, "geography.txt")
VEHICLES_FILE = os.path.join(EXTRA_DATA_DIR, "vehicles.txt")
CUISINE_FILE = os.path.join(EXTRA_DATA_DIR, "cuisine.txt")


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


def test_llama_index_core_importable():
    """SimpleDirectoryReader and Document must be available from llama_index.core."""
    result = subprocess.run(
        [
            "python3",
            "-c",
            "from llama_index.core import SimpleDirectoryReader, Document",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        "Failed to import SimpleDirectoryReader/Document from llama_index.core: "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_initial_data_dir_exists():
    assert os.path.isdir(INITIAL_DATA_DIR), (
        f"Seed initial-data directory {INITIAL_DATA_DIR} does not exist."
    )


def test_extra_data_dir_exists():
    assert os.path.isdir(EXTRA_DATA_DIR), (
        f"Seed extra-data directory {EXTRA_DATA_DIR} does not exist."
    )


def test_animals_file_exists_with_expected_content():
    assert os.path.isfile(ANIMALS_FILE), (
        f"Expected pre-seeded {ANIMALS_FILE} was not found."
    )
    with open(ANIMALS_FILE, "r", encoding="utf-8") as fp:
        content = fp.read()
    assert "Cats are domestic feline mammals known for their independent nature." in content, (
        f"{ANIMALS_FILE} is missing the expected seeded sentence about cats."
    )


def test_geography_file_exists_with_expected_content():
    assert os.path.isfile(GEOGRAPHY_FILE), (
        f"Expected pre-seeded {GEOGRAPHY_FILE} was not found."
    )
    with open(GEOGRAPHY_FILE, "r", encoding="utf-8") as fp:
        content = fp.read()
    assert "Mount Pochi is the tallest mountain on the island of Atlantis." in content, (
        f"{GEOGRAPHY_FILE} is missing the expected seeded sentence about Mount Pochi."
    )


def test_vehicles_file_exists_with_expected_content():
    assert os.path.isfile(VEHICLES_FILE), (
        f"Expected pre-seeded {VEHICLES_FILE} was not found."
    )
    with open(VEHICLES_FILE, "r", encoding="utf-8") as fp:
        content = fp.read()
    assert "The Atlantis Aurora is a flying car invented in 2031 that uses anti-gravity propulsion." in content, (
        f"{VEHICLES_FILE} is missing the expected seeded sentence about the Atlantis Aurora."
    )


def test_cuisine_file_exists_with_expected_content():
    assert os.path.isfile(CUISINE_FILE), (
        f"Expected pre-seeded {CUISINE_FILE} was not found."
    )
    with open(CUISINE_FILE, "r", encoding="utf-8") as fp:
        content = fp.read()
    assert "The national dish of Atlantis is grilled seaweed wrapped around glowing-blue rice." in content, (
        f"{CUISINE_FILE} is missing the expected seeded sentence about Atlantean cuisine."
    )


def test_trial_id_file_exists():
    """The harbor trial_id artifact must exist before the task starts."""
    assert os.path.isfile("/logs/artifacts/trial_id"), (
        "/logs/artifacts/trial_id is missing; cannot scope LlamaCloud resources per trial."
    )


def test_ingest_script_not_pre_created():
    """The executor must create ingest.py; it must not exist initially."""
    ingest_py = os.path.join(PROJECT_DIR, "ingest.py")
    assert not os.path.exists(ingest_py), (
        f"{ingest_py} should not exist at task start; the executor must create it."
    )


def test_output_log_not_pre_created():
    """The executor must create output.log; it must not exist initially."""
    output_log = os.path.join(PROJECT_DIR, "output.log")
    assert not os.path.exists(output_log), (
        f"{output_log} should not exist at task start; the executor must create it."
    )
