import importlib
import os

PROJECT_DIR = "/home/user/tables_task"
SAMPLE_PDF = os.path.join(PROJECT_DIR, "sample.pdf")


def test_llama_cloud_sdk_importable():
    """The official LlamaCloud Python SDK must be available in the environment."""
    module = importlib.import_module("llama_cloud")
    assert module is not None, "llama_cloud SDK is not importable in the task environment."


def test_project_directory_exists():
    """The task workspace must already exist as stated in the task description."""
    assert os.path.isdir(PROJECT_DIR), (
        f"Expected project directory {PROJECT_DIR} to exist as part of the initial state."
    )


def test_sample_pdf_exists():
    """The seeded source PDF must be present before the executor starts."""
    assert os.path.isfile(SAMPLE_PDF), (
        f"Expected seeded PDF {SAMPLE_PDF} to exist as part of the initial state."
    )


def test_sample_pdf_is_non_empty_pdf():
    """The seeded PDF must be a non-empty file with a PDF magic header."""
    size = os.path.getsize(SAMPLE_PDF)
    assert size > 0, f"Expected {SAMPLE_PDF} to be non-empty, got size {size}."
    with open(SAMPLE_PDF, "rb") as handle:
        header = handle.read(5)
    assert header.startswith(b"%PDF-"), (
        f"Expected {SAMPLE_PDF} to start with the PDF magic header, got {header!r}."
    )


def test_llama_cloud_api_key_present():
    """The task requires LLAMA_CLOUD_API_KEY to authenticate against LlamaCloud."""
    assert os.environ.get("LLAMA_CLOUD_API_KEY"), (
        "LLAMA_CLOUD_API_KEY must be set in the task environment for the executor to call LlamaCloud."
    )
