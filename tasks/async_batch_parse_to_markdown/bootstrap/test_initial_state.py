import os
import shutil
import subprocess

PROJECT_DIR = "/home/user/batch_parse"
PDF_DIR = os.path.join(PROJECT_DIR, "pdfs")
OUT_DIR = os.path.join(PROJECT_DIR, "out")
SCRIPT_PATH = os.path.join(PROJECT_DIR, "batch_parse.py")

EXPECTED_PDFS = ("alpha.pdf", "bravo.pdf", "charlie.pdf")


def test_python3_available():
    assert shutil.which("python3") is not None, "python3 binary not found in PATH."


def test_llama_cloud_sdk_importable():
    result = subprocess.run(
        ["python3", "-c", "import llama_cloud; print(llama_cloud.__name__)"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"llama_cloud Python package is not importable. stderr: {result.stderr}"
    )


def test_async_llama_cloud_client_class_available():
    result = subprocess.run(
        [
            "python3",
            "-c",
            "from llama_cloud import AsyncLlamaCloud; print(AsyncLlamaCloud.__name__)",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        "AsyncLlamaCloud client class must be importable from llama_cloud. "
        f"stderr: {result.stderr}"
    )


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Expected project directory {PROJECT_DIR} to exist before task execution."
    )


def test_pdf_directory_exists():
    assert os.path.isdir(PDF_DIR), (
        f"Expected input PDF directory {PDF_DIR} to exist before task execution."
    )


def test_each_initial_pdf_exists_and_is_valid():
    for pdf_name in EXPECTED_PDFS:
        pdf_path = os.path.join(PDF_DIR, pdf_name)
        assert os.path.isfile(pdf_path), (
            f"Expected initial PDF {pdf_path} to exist before task execution."
        )
        assert os.path.getsize(pdf_path) > 0, (
            f"Initial PDF {pdf_path} exists but is empty."
        )
        with open(pdf_path, "rb") as f:
            header = f.read(5)
        assert header.startswith(b"%PDF-"), (
            f"Initial file {pdf_path} does not appear to be a valid PDF "
            "(missing %PDF- header)."
        )


def test_output_directory_not_yet_created():
    assert not os.path.exists(OUT_DIR), (
        f"Output directory {OUT_DIR} must not exist before the task is executed."
    )


def test_batch_parse_script_not_yet_created():
    assert not os.path.exists(SCRIPT_PATH), (
        f"Script {SCRIPT_PATH} must not exist before the task is executed."
    )


def test_llama_cloud_api_key_env_set():
    value = os.environ.get("LLAMA_CLOUD_API_KEY")
    assert value is not None and value.strip() != "", (
        "LLAMA_CLOUD_API_KEY environment variable must be set for the task environment."
    )
