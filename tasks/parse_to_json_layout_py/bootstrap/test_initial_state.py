import importlib
import os

import pytest

PROJECT_DIR = "/home/user/myproject"
SAMPLE_PDF = os.path.join(PROJECT_DIR, "manual.pdf")
TRIAL_ID_PATH = "/logs/artifacts/trial_id"


def test_llama_cloud_services_importable():
    """The `llama_cloud_services` SDK (which exposes LlamaParse) must be importable."""
    try:
        module = importlib.import_module("llama_cloud_services")
    except ImportError as exc:
        pytest.fail(
            "`llama_cloud_services` is not importable: "
            f"{exc}. The LlamaParse Python SDK must be available in the task environment."
        )
    assert module is not None, "Imported `llama_cloud_services` module is None."


def test_project_directory_exists():
    """The project directory specified in the task must exist."""
    assert os.path.isdir(PROJECT_DIR), (
        f"Expected project directory {PROJECT_DIR} to exist before the task starts."
    )


def test_sample_pdf_exists():
    """The pre-staged multi-page sample PDF must exist and be non-empty."""
    assert os.path.isfile(SAMPLE_PDF), (
        f"Expected sample PDF at {SAMPLE_PDF} to exist before the task starts."
    )
    assert os.path.getsize(SAMPLE_PDF) > 0, (
        f"Sample PDF at {SAMPLE_PDF} exists but is empty."
    )


def test_sample_pdf_has_pdf_magic_bytes():
    """The pre-staged sample PDF must start with the `%PDF-` magic header."""
    with open(SAMPLE_PDF, "rb") as f:
        header = f.read(5)
    assert header == b"%PDF-", (
        f"Expected {SAMPLE_PDF} to start with PDF magic bytes `%PDF-`, "
        f"got {header!r}."
    )


def test_llama_cloud_api_key_env_var_is_set():
    """The LlamaCloud API key environment variable must be available to the task."""
    value = os.environ.get("LLAMA_CLOUD_API_KEY")
    assert value, (
        "Environment variable `LLAMA_CLOUD_API_KEY` is not set; the LlamaParse "
        "SDK cannot authenticate without it."
    )


def test_trial_id_file_exists():
    """The trial_id file used for parallel-run isolation must be present."""
    assert os.path.isfile(TRIAL_ID_PATH), (
        f"Expected trial_id file at {TRIAL_ID_PATH} to exist before the task starts."
    )
    with open(TRIAL_ID_PATH, "r", encoding="utf-8") as f:
        content = f.read().strip()
    assert content, f"trial_id file at {TRIAL_ID_PATH} is empty."
