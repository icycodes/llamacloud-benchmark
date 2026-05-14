import os
import shutil
import subprocess

PROJECT_DIR = "/home/user/screenshot_task"
SAMPLE_PDF = os.path.join(PROJECT_DIR, "report.pdf")


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
    assert os.path.isfile(SAMPLE_PDF), \
        f"Source PDF {SAMPLE_PDF} does not exist."


def test_report_pdf_non_empty():
    assert os.path.getsize(SAMPLE_PDF) > 0, \
        f"Source PDF {SAMPLE_PDF} is empty."


def test_report_pdf_signature():
    with open(SAMPLE_PDF, "rb") as f:
        header = f.read(5)
    assert header.startswith(b"%PDF-"), \
        f"Source PDF {SAMPLE_PDF} does not have a valid PDF signature."


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


def test_download_script_not_yet_created():
    # The agent is expected to create this file. It must NOT exist beforehand.
    script_path = os.path.join(PROJECT_DIR, "download_screenshots.py")
    assert not os.path.exists(script_path), \
        f"Initial state should not include {script_path}; it is the agent's job to create it."


def test_screenshots_dir_not_yet_created():
    screenshots_dir = os.path.join(PROJECT_DIR, "screenshots")
    assert not os.path.exists(screenshots_dir), \
        f"Initial state should not include {screenshots_dir}; it is the agent's job to create it."


def test_manifest_json_not_yet_created():
    manifest_path = os.path.join(PROJECT_DIR, "manifest.json")
    assert not os.path.exists(manifest_path), \
        f"Initial state should not include {manifest_path}; it is the agent's job to create it."
