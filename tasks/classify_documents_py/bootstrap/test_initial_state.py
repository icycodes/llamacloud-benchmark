import importlib
import os

import pytest

PROJECT_DIR = "/home/user/myproject"
DOCS_DIR = os.path.join(PROJECT_DIR, "docs")
TRIAL_ID_PATH = "/logs/artifacts/trial_id"

EXPECTED_FIXTURE_FILES = ("invoice.pdf", "receipt.pdf", "contract.pdf")


def test_llama_cloud_sdk_importable():
    """The `llama_cloud` Python SDK must be importable in the task environment."""
    try:
        module = importlib.import_module("llama_cloud")
    except ImportError as exc:
        pytest.fail(
            "`llama_cloud` is not importable: "
            f"{exc}. The LlamaCloud Python SDK must be available in the task "
            "environment for the LlamaClassify workflow."
        )
    assert module is not None, "Imported `llama_cloud` module is None."


def test_project_directory_exists():
    """The project directory specified in the task must exist."""
    assert os.path.isdir(PROJECT_DIR), (
        f"Expected project directory {PROJECT_DIR} to exist before the task starts."
    )


def test_docs_directory_exists():
    """The pre-staged docs directory must exist for the agent to discover input PDFs."""
    assert os.path.isdir(DOCS_DIR), (
        f"Expected docs directory {DOCS_DIR} to exist before the task starts."
    )


@pytest.mark.parametrize("filename", EXPECTED_FIXTURE_FILES)
def test_fixture_pdf_exists_and_non_empty(filename):
    """Every pre-staged fixture PDF must exist and be a non-empty regular file."""
    path = os.path.join(DOCS_DIR, filename)
    assert os.path.isfile(path), (
        f"Expected pre-staged fixture file {path} to exist before the task starts."
    )
    assert os.path.getsize(path) > 0, (
        f"Pre-staged fixture file {path} exists but is empty."
    )


def test_llama_cloud_api_key_env_var_is_set():
    """The LlamaCloud API key environment variable must be available to the task."""
    value = os.environ.get("LLAMA_CLOUD_API_KEY")
    assert value, (
        "Environment variable `LLAMA_CLOUD_API_KEY` is not set; the "
        "LlamaCloud SDK cannot authenticate without it."
    )


def test_trial_id_file_exists():
    """The trial_id file used for parallel-run isolation must be present."""
    assert os.path.isfile(TRIAL_ID_PATH), (
        f"Expected trial_id file at {TRIAL_ID_PATH} to exist before the task starts."
    )
    with open(TRIAL_ID_PATH, "r", encoding="utf-8") as f:
        content = f.read().strip()
    assert content, f"trial_id file at {TRIAL_ID_PATH} is empty."
