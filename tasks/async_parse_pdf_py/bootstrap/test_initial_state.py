import os
import shutil
import subprocess

PROJECT_DIR = "/home/user/myproject"
SAMPLE_PDF = "/home/user/myproject/sample.pdf"


def test_python3_available():
    assert shutil.which("python3") is not None, \
        "python3 binary not found in PATH; it is required to run the LlamaParse async CLI script."


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), \
        f"Project directory {PROJECT_DIR} does not exist; it must be pre-created in the environment."


def test_sample_pdf_exists():
    assert os.path.isfile(SAMPLE_PDF), \
        f"Sample PDF {SAMPLE_PDF} is missing; the initial environment must provide it for the task."


def test_sample_pdf_is_nonempty():
    size = os.path.getsize(SAMPLE_PDF)
    assert size > 0, \
        f"Sample PDF {SAMPLE_PDF} is empty (size={size}); it must contain a real PDF document."


def test_sample_pdf_has_pdf_magic_bytes():
    with open(SAMPLE_PDF, "rb") as fh:
        header = fh.read(5)
    assert header.startswith(b"%PDF-"), \
        f"Sample PDF {SAMPLE_PDF} does not begin with the '%PDF-' magic bytes; it is not a valid PDF."


def test_llama_cloud_sdk_installed():
    """Verify the `llama_cloud` package is importable."""
    result = subprocess.run(
        ["python3", "-c", "import llama_cloud; print(llama_cloud.__name__)"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, \
        f"`llama_cloud` Python package is not importable. stderr: {result.stderr}"
    assert "llama_cloud" in result.stdout, \
        f"Expected 'llama_cloud' module to be importable; got stdout: {result.stdout!r}"


def test_async_llama_cloud_class_importable():
    """Verify the asynchronous `AsyncLlamaCloud` client class is importable."""
    result = subprocess.run(
        [
            "python3",
            "-c",
            "from llama_cloud import AsyncLlamaCloud; print('ok')",
        ],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, (
        "Failed to import AsyncLlamaCloud from `llama_cloud`: "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "ok" in result.stdout, (
        "Expected 'ok' to be printed when importing AsyncLlamaCloud, "
        f"got stdout={result.stdout!r}"
    )


def test_llama_cloud_api_key_present_in_env():
    assert os.environ.get("LLAMA_CLOUD_API_KEY"), \
        "LLAMA_CLOUD_API_KEY environment variable must be set so the SDK can authenticate against LlamaCloud."
