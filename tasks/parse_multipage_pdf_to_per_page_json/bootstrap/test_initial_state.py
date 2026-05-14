import os
import shutil
import subprocess
import pytest

PROJECT_DIR = "/home/user/myproject"
REPORT_PDF = os.path.join(PROJECT_DIR, "report.pdf")


def test_python3_available():
    assert shutil.which("python3") is not None, \
        "python3 binary not found in PATH."


def test_pip3_available():
    assert shutil.which("pip3") is not None, \
        "pip3 binary not found in PATH."


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), \
        f"Project directory {PROJECT_DIR} does not exist."


def test_report_pdf_exists():
    assert os.path.isfile(REPORT_PDF), \
        f"Source PDF {REPORT_PDF} does not exist."


def test_report_pdf_non_empty():
    assert os.path.getsize(REPORT_PDF) > 0, \
        f"Source PDF {REPORT_PDF} is empty."


def test_report_pdf_signature():
    with open(REPORT_PDF, "rb") as f:
        header = f.read(5)
    assert header.startswith(b"%PDF-"), \
        f"Source PDF {REPORT_PDF} does not have a valid PDF signature."


def test_llama_cloud_services_installed():
    result = subprocess.run(
        ["python3", "-c", "import llama_cloud_services"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, \
        f"Python package 'llama_cloud_services' is not importable. stderr: {result.stderr}"


def test_llama_cloud_installed():
    result = subprocess.run(
        ["python3", "-c", "import llama_cloud"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, \
        f"Python package 'llama_cloud' is not importable. stderr: {result.stderr}"


def test_llama_cloud_api_key_env_var_present():
    api_key = os.environ.get("LLAMA_CLOUD_API_KEY")
    assert api_key is not None and api_key.strip() != "", \
        "LLAMA_CLOUD_API_KEY environment variable is not set."


def test_parse_pages_script_not_yet_created():
    parse_script = os.path.join(PROJECT_DIR, "parse_pages.py")
    assert not os.path.exists(parse_script), \
        f"Initial state should not include {parse_script}; it is the agent's job to create it."


def test_pages_json_not_yet_created():
    pages_json = os.path.join(PROJECT_DIR, "pages.json")
    assert not os.path.exists(pages_json), \
        f"Initial state should not include {pages_json}; it is the agent's job to create it."
