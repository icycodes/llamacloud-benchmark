import importlib
import os


PROJECT_DIR = "/home/user/extract_task"
SAMPLE_PDF = os.path.join(PROJECT_DIR, "sample.pdf")


def test_llama_cloud_sdk_importable():
    """The official LlamaCloud Python SDK must be importable in the task environment."""
    module = importlib.import_module("llama_cloud")
    assert module is not None, "Expected the `llama_cloud` Python package to be importable."


def test_pydantic_available():
    """Pydantic must be available for defining the extraction schema."""
    module = importlib.import_module("pydantic")
    assert module is not None, "Expected the `pydantic` Python package to be importable."


def test_project_dir_exists():
    """The project working directory must exist before the task starts."""
    assert os.path.isdir(PROJECT_DIR), (
        f"Expected project directory {PROJECT_DIR} to exist before the task starts."
    )


def test_sample_pdf_exists():
    """The source PDF used as the extraction input must be seeded."""
    assert os.path.isfile(SAMPLE_PDF), (
        f"Expected source PDF {SAMPLE_PDF} to be seeded before the task starts."
    )
    # The PDF must be non-trivially sized to ensure it is a real PDF, not an empty placeholder.
    assert os.path.getsize(SAMPLE_PDF) > 256, (
        f"Expected {SAMPLE_PDF} to be a non-empty PDF (size > 256 bytes)."
    )


def test_sample_pdf_has_pdf_header():
    """The source PDF must have a valid PDF header so LlamaExtract can parse it."""
    with open(SAMPLE_PDF, "rb") as fh:
        header = fh.read(5)
    assert header == b"%PDF-", (
        f"Expected {SAMPLE_PDF} to start with the `%PDF-` magic bytes, got: {header!r}."
    )


def test_llama_cloud_api_key_env_set():
    """The LLAMA_CLOUD_API_KEY environment variable must be available for LlamaCloud calls."""
    value = os.environ.get("LLAMA_CLOUD_API_KEY")
    assert value, "Expected LLAMA_CLOUD_API_KEY to be set in the task execution environment."
