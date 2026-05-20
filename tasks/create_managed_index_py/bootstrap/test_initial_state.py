import importlib
import os

import pytest

PROJECT_DIR = "/home/user/myproject"
DATA_DIR = os.path.join(PROJECT_DIR, "data")


def test_llama_cloud_index_importable():
    try:
        importlib.import_module("llama_index.indices.managed.llama_cloud")
    except ImportError as exc:  # pragma: no cover
        pytest.fail(
            "Expected `llama_index.indices.managed.llama_cloud` to be importable, "
            f"but import failed: {exc}"
        )


def test_llama_index_core_importable():
    try:
        importlib.import_module("llama_index.core")
    except ImportError as exc:  # pragma: no cover
        pytest.fail(
            "Expected `llama_index.core` to be importable, but import failed: "
            f"{exc}"
        )


def test_llama_cloud_api_key_env_var_set():
    api_key = os.environ.get("LLAMA_CLOUD_API_KEY")
    assert api_key, (
        "Environment variable LLAMA_CLOUD_API_KEY must be set in the task "
        "environment."
    )


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Expected project directory to exist at {PROJECT_DIR}."
    )


def test_data_dir_exists():
    assert os.path.isdir(DATA_DIR), (
        f"Expected data directory to exist at {DATA_DIR}."
    )


@pytest.mark.parametrize("filename", ["cats.txt", "dogs.txt", "birds.txt"])
def test_seed_document_exists(filename):
    file_path = os.path.join(DATA_DIR, filename)
    assert os.path.isfile(file_path), (
        f"Expected seed document {file_path} to be present in the initial "
        "environment."
    )
    assert os.path.getsize(file_path) > 0, (
        f"Seed document {file_path} must not be empty."
    )


def test_trial_id_file_present():
    trial_id_path = "/logs/artifacts/trial_id"
    assert os.path.isfile(trial_id_path), (
        f"Expected trial id file at {trial_id_path} to be provided by Harbor."
    )
    with open(trial_id_path) as f:
        trial_id = f.read().strip()
    assert trial_id, "trial_id file must not be empty."
