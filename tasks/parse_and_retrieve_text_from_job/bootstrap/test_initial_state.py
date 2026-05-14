import os
import shutil
import subprocess
import pytest

PROJECT_DIR = "/home/user/llama_task"
REPORT_PDF = os.path.join(PROJECT_DIR, "report.pdf")
OUTPUT_MD = os.path.join(PROJECT_DIR, "output.md")
OUTPUT_TXT = os.path.join(PROJECT_DIR, "output.txt")
JOB_ID_FILE = os.path.join(PROJECT_DIR, "job_id.txt")
SCRIPT_PATH = os.path.join(PROJECT_DIR, "parse_and_retrieve.py")


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
        f"LlamaCloud client class is not importable from llama_cloud. "
        f"stderr: {result.stderr}"
    )


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Expected project directory {PROJECT_DIR} to exist before task execution."
    )


def test_report_pdf_exists():
    assert os.path.isfile(REPORT_PDF), (
        f"Expected initial PDF file {REPORT_PDF} to exist before task execution."
    )


def test_report_pdf_is_nonempty():
    assert os.path.getsize(REPORT_PDF) > 0, (
        f"Initial PDF file {REPORT_PDF} must be non-empty."
    )


def test_report_pdf_is_valid_pdf():
    with open(REPORT_PDF, "rb") as f:
        header = f.read(5)
    assert header.startswith(b"%PDF-"), (
        f"Initial file {REPORT_PDF} does not appear to be a valid PDF "
        f"(missing %PDF- header)."
    )


def test_script_not_yet_created():
    assert not os.path.exists(SCRIPT_PATH), (
        f"Script {SCRIPT_PATH} must not exist before the task is executed."
    )


def test_output_md_not_yet_created():
    assert not os.path.exists(OUTPUT_MD), (
        f"Output file {OUTPUT_MD} must not exist before the task is executed."
    )


def test_output_txt_not_yet_created():
    assert not os.path.exists(OUTPUT_TXT), (
        f"Output file {OUTPUT_TXT} must not exist before the task is executed."
    )


def test_job_id_file_not_yet_created():
    assert not os.path.exists(JOB_ID_FILE), (
        f"Output file {JOB_ID_FILE} must not exist before the task is executed."
    )


def test_llama_cloud_api_key_env_set():
    value = os.environ.get("LLAMA_CLOUD_API_KEY")
    assert value is not None and value.strip() != "", (
        "LLAMA_CLOUD_API_KEY environment variable must be set for the task environment."
    )
