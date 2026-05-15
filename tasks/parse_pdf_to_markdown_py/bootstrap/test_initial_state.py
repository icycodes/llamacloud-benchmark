import os
import shutil
import subprocess

PROJECT_DIR = "/home/user/parse_task"
SAMPLE_PDF = os.path.join(PROJECT_DIR, "sample.pdf")


def test_python3_available():
    assert shutil.which("python3") is not None, "python3 binary not found in PATH."


def test_llama_cloud_sdk_importable():
    """The LlamaCloud Python SDK must already be installed."""
    result = subprocess.run(
        ["python3", "-c", "import llama_cloud"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Failed to import llama_cloud: stdout={result.stdout!r} stderr={result.stderr!r}"
    )


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_sample_pdf_exists():
    assert os.path.isfile(SAMPLE_PDF), (
        f"Expected pre-seeded PDF at {SAMPLE_PDF} was not found."
    )


def test_sample_pdf_is_a_pdf():
    """Verify the seeded file is a real PDF (magic bytes)."""
    with open(SAMPLE_PDF, "rb") as fp:
        header = fp.read(4)
    assert header == b"%PDF", (
        f"File at {SAMPLE_PDF} does not look like a PDF (got header {header!r})."
    )


def test_output_md_not_pre_created():
    """The executor must create the output file; it must not exist initially."""
    output_md = os.path.join(PROJECT_DIR, "output.md")
    assert not os.path.exists(output_md), (
        f"{output_md} should not exist at task start; the executor must create it."
    )


def test_parse_script_not_pre_created():
    """The executor must create parse.py; it must not exist initially."""
    parse_py = os.path.join(PROJECT_DIR, "parse.py")
    assert not os.path.exists(parse_py), (
        f"{parse_py} should not exist at task start; the executor must create it."
    )
