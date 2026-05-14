import os
import shutil
import subprocess
import pytest

PROJECT_DIR = "/home/user/catalog_task"
CATALOG_PDF = os.path.join(PROJECT_DIR, "catalog.pdf")
OUTPUT_MD = os.path.join(PROJECT_DIR, "selected_pages.md")
SCRIPT_PATH = os.path.join(PROJECT_DIR, "parse_selected.py")


def test_python3_available():
    assert shutil.which("python3") is not None, "python3 binary not found in PATH."


def test_llama_cloud_sdk_installed():
    result = subprocess.run(
        ["python3", "-c", "import llama_cloud; print(llama_cloud.__name__)"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"llama_cloud Python package is not importable. stderr: {result.stderr}"
    )


def test_llama_cloud_client_class_available():
    result = subprocess.run(
        [
            "python3",
            "-c",
            "from llama_cloud import LlamaCloud; print(LlamaCloud.__name__)",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"LlamaCloud client class is not importable from llama_cloud. stderr: {result.stderr}"
    )


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Expected project directory {PROJECT_DIR} to exist before task execution."
    )


def test_catalog_pdf_exists():
    assert os.path.isfile(CATALOG_PDF), (
        f"Expected initial PDF file {CATALOG_PDF} to exist before task execution."
    )


def test_catalog_pdf_is_nonempty():
    assert os.path.getsize(CATALOG_PDF) > 0, (
        f"Initial PDF file {CATALOG_PDF} must be non-empty."
    )


def test_catalog_pdf_is_valid_pdf():
    with open(CATALOG_PDF, "rb") as f:
        header = f.read(5)
    assert header.startswith(b"%PDF-"), (
        f"Initial file {CATALOG_PDF} does not appear to be a valid PDF (missing %PDF- header)."
    )


def test_catalog_pdf_has_four_pages():
    """The initial PDF is expected to be a 4-page document so we can target only pages 1 and 3."""
    with open(CATALOG_PDF, "rb") as f:
        content = f.read()
    # Count PDF page objects. /Type /Page (but not /Pages) appears once per page.
    # This is a quick heuristic; reportlab-built PDFs match this pattern reliably.
    page_markers = content.count(b"/Type /Page")
    # Exclude /Type /Pages (catalog) entries
    pages_root = content.count(b"/Type /Pages")
    actual_pages = page_markers - pages_root
    assert actual_pages == 4, (
        f"Expected {CATALOG_PDF} to be a 4-page PDF, but counted {actual_pages} page object(s)."
    )


def test_output_md_not_yet_created():
    assert not os.path.exists(OUTPUT_MD), (
        f"Output file {OUTPUT_MD} must not exist before the task is executed."
    )


def test_parse_script_not_yet_created():
    assert not os.path.exists(SCRIPT_PATH), (
        f"Script {SCRIPT_PATH} must not exist before the task is executed."
    )


def test_llama_cloud_api_key_env_set():
    value = os.environ.get("LLAMA_CLOUD_API_KEY")
    assert value is not None and value.strip() != "", (
        "LLAMA_CLOUD_API_KEY environment variable must be set for the task environment."
    )
