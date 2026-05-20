import os
import shutil

import pytest

PROJECT_DIR = "/home/user/screenshot_task"
SAMPLE_PDF = os.path.join(PROJECT_DIR, "sample.pdf")
TRIAL_ID_PATH = "/logs/artifacts/trial_id"


def test_python3_available():
    assert shutil.which("python3") is not None, "python3 binary not found in PATH."


def test_llama_cloud_sdk_importable():
    try:
        import llama_cloud  # noqa: F401
    except Exception as exc:  # pragma: no cover - import error surfaces immediately
        pytest.fail(f"Failed to import the llama_cloud Python SDK: {exc}")


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_sample_pdf_exists():
    assert os.path.isfile(SAMPLE_PDF), (
        f"Seeded source PDF {SAMPLE_PDF} does not exist."
    )


def test_sample_pdf_is_a_real_pdf():
    with open(SAMPLE_PDF, "rb") as fp:
        header = fp.read(5)
    assert header == b"%PDF-", (
        f"Seeded {SAMPLE_PDF} does not start with the %PDF- header; got {header!r}."
    )


def test_trial_id_artifact_present():
    assert os.path.isfile(TRIAL_ID_PATH), (
        f"Trial id artifact missing at {TRIAL_ID_PATH}."
    )
    with open(TRIAL_ID_PATH, "r", encoding="utf-8") as fp:
        trial_id = fp.read().strip()
    assert trial_id, f"Trial id at {TRIAL_ID_PATH} is empty."


def test_llama_cloud_api_key_env():
    assert os.environ.get("LLAMA_CLOUD_API_KEY"), (
        "LLAMA_CLOUD_API_KEY is not set in the task environment."
    )
