import importlib
import os

import pytest

PROJECT_DIR = "/home/user/parse_bytes_task"
DOCS_DIR = os.path.join(PROJECT_DIR, "docs")
EXPECTED_PDFS = [
    "alpha_report.pdf",
    "beta_invoice.pdf",
    "gamma_memo.pdf",
]


def test_llama_cloud_services_importable():
    """The LlamaCloud parsing client must be installed."""
    try:
        module = importlib.import_module("llama_cloud_services")
    except Exception as exc:
        pytest.fail(
            f"Expected 'llama_cloud_services' Python package to be importable, "
            f"but importing it failed: {exc!r}"
        )
    assert hasattr(module, "LlamaParse"), (
        "Expected 'LlamaParse' to be exposed from the llama_cloud_services package."
    )


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Expected project directory {PROJECT_DIR} to exist before the task starts."
    )


def test_docs_directory_exists():
    assert os.path.isdir(DOCS_DIR), (
        f"Expected input docs directory {DOCS_DIR} to exist before the task starts."
    )


@pytest.mark.parametrize("pdf_name", EXPECTED_PDFS)
def test_seed_pdf_exists_and_is_nonempty(pdf_name):
    pdf_path = os.path.join(DOCS_DIR, pdf_name)
    assert os.path.isfile(pdf_path), (
        f"Expected seeded PDF {pdf_path} to exist before the task starts."
    )
    assert os.path.getsize(pdf_path) > 0, (
        f"Expected seeded PDF {pdf_path} to be non-empty before the task starts."
    )


@pytest.mark.parametrize("pdf_name", EXPECTED_PDFS)
def test_seed_pdf_has_pdf_signature(pdf_name):
    """Quick sanity-check that the seeded fixtures are actually PDFs."""
    pdf_path = os.path.join(DOCS_DIR, pdf_name)
    with open(pdf_path, "rb") as fp:
        header = fp.read(4)
    assert header == b"%PDF", (
        f"Expected file {pdf_path} to start with the %PDF signature, got {header!r}."
    )
