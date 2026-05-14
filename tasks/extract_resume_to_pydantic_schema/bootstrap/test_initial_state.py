import os
import shutil
import subprocess
import pytest

PROJECT_DIR = "/home/user/resume_extract"
RESUME_PATH = os.path.join(PROJECT_DIR, "resume.txt")
SCRIPT_PATH = os.path.join(PROJECT_DIR, "extract_resume.py")
OUTPUT_PATH = os.path.join(PROJECT_DIR, "extracted.json")


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
    assert "LlamaCloud" in result.stdout, (
        f"Expected 'LlamaCloud' to be the class name. stdout: {result.stdout!r}"
    )


def test_pydantic_v2_installed():
    result = subprocess.run(
        [
            "python3",
            "-c",
            "import pydantic; "
            "assert int(pydantic.VERSION.split('.')[0]) >= 2, pydantic.VERSION; "
            "from pydantic import BaseModel, Field; print('ok')",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"pydantic v2 (with BaseModel and Field) must be importable. "
        f"stderr: {result.stderr}"
    )
    assert "ok" in result.stdout, f"Pydantic check did not print 'ok'. stdout: {result.stdout!r}"


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Expected project directory {PROJECT_DIR} to exist before task execution."
    )


def test_resume_file_exists():
    assert os.path.isfile(RESUME_PATH), (
        f"Expected pre-existing resume file {RESUME_PATH} before the task is executed."
    )


def test_resume_contents_match_expected():
    with open(RESUME_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    assert "Candidate Name: Jane Doe" in content, (
        f"Expected the candidate name line in {RESUME_PATH}."
    )
    assert "Email: jane.doe@example.com" in content, (
        f"Expected the candidate email line in {RESUME_PATH}."
    )
    assert "Technical Skills:" in content, (
        f"Expected a 'Technical Skills:' line in {RESUME_PATH}."
    )


def test_llama_cloud_api_key_env_set():
    value = os.environ.get("LLAMA_CLOUD_API_KEY")
    assert value is not None and value.strip() != "", (
        "LLAMA_CLOUD_API_KEY environment variable must be set for the task environment."
    )


def test_extract_script_not_yet_created():
    assert not os.path.exists(SCRIPT_PATH), (
        f"Script {SCRIPT_PATH} must not exist before the task is executed."
    )


def test_extracted_output_not_yet_created():
    assert not os.path.exists(OUTPUT_PATH), (
        f"Output file {OUTPUT_PATH} must not exist before the task is executed."
    )
