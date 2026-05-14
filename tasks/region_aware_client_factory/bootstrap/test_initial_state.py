import os
import shutil
import subprocess
import pytest

PROJECT_DIR = "/home/user/region_setup"
CLIENT_FACTORY_PATH = os.path.join(PROJECT_DIR, "client_factory.py")
RUN_PATH = os.path.join(PROJECT_DIR, "run.py")
RESOLVED_NA_PATH = os.path.join(PROJECT_DIR, "resolved_na.json")
RESOLVED_EU_PATH = os.path.join(PROJECT_DIR, "resolved_eu.json")


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
    assert "LlamaCloud" in result.stdout, (
        f"Expected 'LlamaCloud' to be the class name. stdout: {result.stdout!r}"
    )


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Expected project directory {PROJECT_DIR} to exist before task execution."
    )


def test_llama_cloud_api_key_env_set():
    value = os.environ.get("LLAMA_CLOUD_API_KEY")
    assert value is not None and value.strip() != "", (
        "LLAMA_CLOUD_API_KEY environment variable must be set for the task environment."
    )


def test_client_factory_not_yet_created():
    assert not os.path.exists(CLIENT_FACTORY_PATH), (
        f"Module {CLIENT_FACTORY_PATH} must not exist before the task is executed."
    )


def test_run_script_not_yet_created():
    assert not os.path.exists(RUN_PATH), (
        f"Runner script {RUN_PATH} must not exist before the task is executed."
    )


def test_resolved_na_json_not_yet_created():
    assert not os.path.exists(RESOLVED_NA_PATH), (
        f"Output file {RESOLVED_NA_PATH} must not exist before the task is executed."
    )


def test_resolved_eu_json_not_yet_created():
    assert not os.path.exists(RESOLVED_EU_PATH), (
        f"Output file {RESOLVED_EU_PATH} must not exist before the task is executed."
    )
