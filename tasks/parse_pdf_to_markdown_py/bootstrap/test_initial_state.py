import importlib
import os

PROJECT_DIR = "/home/user/myproject"
PDF_PATH = os.path.join(PROJECT_DIR, "quarterly_report.pdf")


def test_llama_cloud_sdk_importable():
    """The official `llama-cloud` Python SDK must be installed in the environment."""
    module = importlib.import_module("llama_cloud")
    assert module is not None, "Failed to import the llama_cloud SDK."


def test_llama_cloud_api_key_env_var_present():
    """LlamaCloud requires LLAMA_CLOUD_API_KEY to authenticate requests."""
    value = os.environ.get("LLAMA_CLOUD_API_KEY")
    assert value, "Environment variable LLAMA_CLOUD_API_KEY must be set for the task."


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), f"Expected project directory {PROJECT_DIR} to exist."


def test_input_pdf_exists():
    assert os.path.isfile(PDF_PATH), f"Expected input PDF at {PDF_PATH} to exist."


def test_input_pdf_is_non_empty_pdf():
    """Sanity check that the seeded file is a real, non-empty PDF."""
    assert os.path.getsize(PDF_PATH) > 0, f"Input PDF {PDF_PATH} must not be empty."
    with open(PDF_PATH, "rb") as handle:
        header = handle.read(5)
    assert header.startswith(b"%PDF-"), (
        f"Input PDF {PDF_PATH} does not start with the %PDF- magic header."
    )
