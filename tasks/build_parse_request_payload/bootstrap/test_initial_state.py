import json
import os
import shutil
import subprocess

import pytest

PROJECT_DIR = "/home/user/parse_payload"
INTENT_PATH = os.path.join(PROJECT_DIR, "intent.json")
SCRIPT_PATH = os.path.join(PROJECT_DIR, "build_payload.py")
OUTPUT_PATH = os.path.join(PROJECT_DIR, "request_body.json")

EXPECTED_INTENT = {
    "file_id": "file-demo-abc-123",
    "tier": "agentic",
    "version": "latest",
    "pages": "1-3,5",
    "crop_top": 0.1,
    "crop_bottom": 0.15,
    "ocr_languages": ["en", "fr"],
    "tables_as_html": True,
    "save_screenshots": True,
    "custom_prompt": "This is a financial report. Preserve currency symbols.",
    "enable_cost_optimizer": True,
    "base_timeout_seconds": 300,
    "extra_time_per_page_seconds": 30,
    "ignore_diagonal_text": True,
    "disable_cache": False,
}


def test_python3_available():
    assert shutil.which("python3") is not None, "python3 binary not found in PATH."


def test_llama_cloud_sdk_importable():
    result = subprocess.run(
        ["python3", "-c", "import llama_cloud; print(llama_cloud.__name__)"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"llama_cloud Python package is not importable. stderr: {result.stderr!r}"
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
        f"stderr: {result.stderr!r}"
    )
    assert "LlamaCloud" in result.stdout, (
        f"Expected the imported class name to be 'LlamaCloud'. stdout: {result.stdout!r}"
    )


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Expected project directory {PROJECT_DIR} to exist before task execution."
    )


def test_intent_file_exists():
    assert os.path.isfile(INTENT_PATH), (
        f"Expected pre-existing intent file {INTENT_PATH}."
    )


def test_intent_file_is_valid_json():
    with open(INTENT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, dict), (
        f"{INTENT_PATH} must contain a JSON object. Got: {type(data).__name__}"
    )


def test_intent_file_contents_match_expected():
    with open(INTENT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data == EXPECTED_INTENT, (
        f"{INTENT_PATH} does not match the expected intent fixture.\n"
        f"Expected: {EXPECTED_INTENT!r}\nGot: {data!r}"
    )


def test_llama_cloud_api_key_env_set():
    value = os.environ.get("LLAMA_CLOUD_API_KEY")
    assert value is not None and value.strip() != "", (
        "LLAMA_CLOUD_API_KEY environment variable must be set for the task environment."
    )


def test_build_payload_script_not_yet_created():
    assert not os.path.exists(SCRIPT_PATH), (
        f"Script {SCRIPT_PATH} must not exist before the task is executed."
    )


def test_request_body_not_yet_created():
    assert not os.path.exists(OUTPUT_PATH), (
        f"Output file {OUTPUT_PATH} must not exist before the task is executed."
    )
