import importlib
import os

PROJECT_DIR = "/home/user/myproject"
SAMPLE_RESUME_PATH = os.path.join(PROJECT_DIR, "sample_resume.txt")
TRIAL_ID_PATH = "/logs/artifacts/trial_id"


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_sample_resume_file_exists():
    assert os.path.isfile(SAMPLE_RESUME_PATH), (
        f"Sample resume file {SAMPLE_RESUME_PATH} does not exist."
    )


def test_sample_resume_contains_expected_content():
    with open(SAMPLE_RESUME_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    assert "John Smith" in content, (
        "Expected the sample resume to contain the candidate name 'John Smith'."
    )
    assert "john.smith@example.com" in content, (
        "Expected the sample resume to contain the candidate email "
        "'john.smith@example.com'."
    )
    for skill in ("Python", "Go", "Kubernetes"):
        assert skill in content, (
            f"Expected the sample resume to list the skill '{skill}'."
        )


def test_llama_cloud_services_importable():
    try:
        importlib.import_module("llama_cloud_services")
    except ImportError as exc:
        raise AssertionError(
            "The 'llama_cloud_services' package must be installed in the "
            f"environment: {exc}"
        )


def test_llama_cloud_sdk_importable():
    try:
        importlib.import_module("llama_cloud")
    except ImportError as exc:
        raise AssertionError(
            "The 'llama_cloud' package must be installed in the environment: "
            f"{exc}"
        )


def test_llama_cloud_api_key_env_is_set():
    api_key = os.environ.get("LLAMA_CLOUD_API_KEY")
    assert api_key, (
        "Environment variable LLAMA_CLOUD_API_KEY must be set before the "
        "task starts."
    )


def test_trial_id_file_exists():
    assert os.path.isfile(TRIAL_ID_PATH), (
        f"Trial id file {TRIAL_ID_PATH} must exist before the task starts."
    )
    with open(TRIAL_ID_PATH, "r", encoding="utf-8") as f:
        trial_id = f.read().strip()
    assert trial_id, "Trial id file must not be empty."
