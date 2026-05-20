import importlib
import os

PROJECT_DIR = "/home/user/myproject"
DATA_DIR = os.path.join(PROJECT_DIR, "data")
ALPHA_PATH = os.path.join(DATA_DIR, "alpha.txt")
BETA_PATH = os.path.join(DATA_DIR, "beta.txt")
TRIAL_ID_PATH = "/logs/artifacts/trial_id"


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_data_directory_exists():
    assert os.path.isdir(DATA_DIR), (
        f"Seed data directory {DATA_DIR} does not exist."
    )


def test_alpha_file_exists():
    assert os.path.isfile(ALPHA_PATH), (
        f"Seed file {ALPHA_PATH} does not exist."
    )


def test_beta_file_exists():
    assert os.path.isfile(BETA_PATH), (
        f"Seed file {BETA_PATH} does not exist."
    )


def test_alpha_file_has_content():
    with open(ALPHA_PATH, "r", encoding="utf-8") as f:
        content = f.read().strip()
    assert content, f"Seed file {ALPHA_PATH} must not be empty."


def test_beta_file_has_content():
    with open(BETA_PATH, "r", encoding="utf-8") as f:
        content = f.read().strip()
    assert content, f"Seed file {BETA_PATH} must not be empty."


def test_data_directory_has_no_extra_files():
    entries = sorted(os.listdir(DATA_DIR))
    assert entries == ["alpha.txt", "beta.txt"], (
        "Expected the seed data directory to contain exactly 'alpha.txt' and "
        f"'beta.txt' before the task starts; got {entries}."
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
