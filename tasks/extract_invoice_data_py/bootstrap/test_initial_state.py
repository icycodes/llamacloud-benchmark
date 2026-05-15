import os
import shutil
import subprocess

PROJECT_DIR = "/home/user/extract_task"
INVOICE_PDF = os.path.join(PROJECT_DIR, "invoice.pdf")


def test_python3_available():
    assert shutil.which("python3") is not None, "python3 binary not found in PATH."


def test_llama_cloud_sdk_importable():
    """The LlamaCloud Python SDK (which exposes LlamaExtract) must be installed."""
    result = subprocess.run(
        ["python3", "-c", "from llama_cloud import LlamaCloud"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        "Failed to import LlamaCloud from llama_cloud: "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )


def test_pydantic_importable():
    """Pydantic must be available so the executor can define the Invoice schema."""
    result = subprocess.run(
        ["python3", "-c", "from pydantic import BaseModel, Field"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        "Failed to import BaseModel/Field from pydantic: "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_invoice_pdf_exists():
    assert os.path.isfile(INVOICE_PDF), (
        f"Expected pre-seeded invoice PDF at {INVOICE_PDF} was not found."
    )


def test_invoice_pdf_is_a_pdf():
    """Verify the seeded file is a real PDF (magic bytes)."""
    with open(INVOICE_PDF, "rb") as fp:
        header = fp.read(4)
    assert header == b"%PDF", (
        f"File at {INVOICE_PDF} does not look like a PDF (got header {header!r})."
    )


def test_trial_id_file_exists():
    """The harbor trial_id artifact must exist before the task starts."""
    assert os.path.isfile("/logs/artifacts/trial_id"), (
        "/logs/artifacts/trial_id is missing; cannot scope LlamaCloud resources per trial."
    )


def test_extract_script_not_pre_created():
    """The executor must create extract.py; it must not exist initially."""
    extract_py = os.path.join(PROJECT_DIR, "extract.py")
    assert not os.path.exists(extract_py), (
        f"{extract_py} should not exist at task start; the executor must create it."
    )


def test_output_json_not_pre_created():
    """The executor must create output.json; it must not exist initially."""
    output_json = os.path.join(PROJECT_DIR, "output.json")
    assert not os.path.exists(output_json), (
        f"{output_json} should not exist at task start; the executor must create it."
    )


def test_output_log_not_pre_created():
    """The executor must create output.log; it must not exist initially."""
    output_log = os.path.join(PROJECT_DIR, "output.log")
    assert not os.path.exists(output_log), (
        f"{output_log} should not exist at task start; the executor must create it."
    )
