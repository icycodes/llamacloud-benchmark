import importlib
import os

import pytest

PROJECT_DIR = "/home/user/myproject"
SAMPLE_PDF = os.path.join(PROJECT_DIR, "invoice.pdf")
TRIAL_ID_PATH = "/logs/artifacts/trial_id"


def test_llama_cloud_sdk_importable():
    """The `llama_cloud` Python SDK must be importable in the task environment."""
    try:
        module = importlib.import_module("llama_cloud")
    except ImportError as exc:
        pytest.fail(
            f"`llama_cloud` package is not importable: {exc}. "
            "The LlamaCloud SDK must be available in the task environment."
        )
    assert module is not None, "Imported `llama_cloud` module is None."


def test_pydantic_importable():
    """The `pydantic` package must be importable so the agent can build a schema."""
    try:
        module = importlib.import_module("pydantic")
    except ImportError as exc:
        pytest.fail(
            f"`pydantic` package is not importable: {exc}. "
            "`pydantic` is required to define the extraction schema."
        )
    assert module is not None, "Imported `pydantic` module is None."


def test_project_directory_exists():
    """The project directory specified in the task must exist."""
    assert os.path.isdir(PROJECT_DIR), (
        f"Expected project directory {PROJECT_DIR} to exist before the task starts."
    )


def test_sample_invoice_pdf_exists():
    """The pre-staged sample invoice PDF that the agent will extract from must exist."""
    assert os.path.isfile(SAMPLE_PDF), (
        f"Expected sample PDF at {SAMPLE_PDF} to be present before the task starts."
    )
    assert os.path.getsize(SAMPLE_PDF) > 0, (
        f"Sample PDF at {SAMPLE_PDF} is empty; it must contain real PDF content."
    )


def test_sample_invoice_pdf_has_pdf_magic_header():
    """invoice.pdf should start with the standard `%PDF-` magic header."""
    with open(SAMPLE_PDF, "rb") as f:
        head = f.read(5)
    assert head == b"%PDF-", (
        f"Expected {SAMPLE_PDF} to start with the PDF magic header `%PDF-`, "
        f"but got: {head!r}."
    )


def test_llama_cloud_api_key_env_var_is_set():
    """The LlamaCloud API key environment variable must be available to the task."""
    value = os.environ.get("LLAMA_CLOUD_API_KEY")
    assert value, (
        "Environment variable `LLAMA_CLOUD_API_KEY` is not set; "
        "LlamaExtract cannot authenticate without it."
    )


def test_trial_id_file_exists():
    """The trial_id file used for parallel-run isolation must be present."""
    assert os.path.isfile(TRIAL_ID_PATH), (
        f"Expected trial_id file at {TRIAL_ID_PATH} to exist before the task starts."
    )
    with open(TRIAL_ID_PATH, "r", encoding="utf-8") as f:
        content = f.read().strip()
    assert content, f"trial_id file at {TRIAL_ID_PATH} is empty."
