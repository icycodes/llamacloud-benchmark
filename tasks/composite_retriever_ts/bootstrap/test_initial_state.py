import os
import shutil
import subprocess

PROJECT_DIR = "/home/user/composite_retriever"
POLICIES_DIR = os.path.join(PROJECT_DIR, "data", "policies")
FAQ_DIR = os.path.join(PROJECT_DIR, "data", "faq")
TRIAL_ID_PATH = "/logs/artifacts/trial_id"


def test_node_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."


def test_npx_available():
    assert shutil.which("npx") is not None, "npx binary not found in PATH."


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."


def test_policies_data_dir_exists():
    assert os.path.isdir(POLICIES_DIR), (
        f"Expected policies data directory {POLICIES_DIR} to exist with sample files."
    )
    files = [f for f in os.listdir(POLICIES_DIR) if os.path.isfile(os.path.join(POLICIES_DIR, f))]
    assert len(files) > 0, f"Expected at least one file under {POLICIES_DIR}."


def test_faq_data_dir_exists():
    assert os.path.isdir(FAQ_DIR), (
        f"Expected FAQ data directory {FAQ_DIR} to exist with sample files."
    )
    files = [f for f in os.listdir(FAQ_DIR) if os.path.isfile(os.path.join(FAQ_DIR, f))]
    assert len(files) > 0, f"Expected at least one file under {FAQ_DIR}."


def test_llama_cloud_api_key_set():
    value = os.environ.get("LLAMA_CLOUD_API_KEY")
    assert value, "LLAMA_CLOUD_API_KEY environment variable must be set."


def test_openai_api_key_set():
    value = os.environ.get("OPENAI_API_KEY")
    assert value, "OPENAI_API_KEY environment variable must be set."


def test_trial_id_file_exists():
    assert os.path.isfile(TRIAL_ID_PATH), (
        f"Trial id file {TRIAL_ID_PATH} must exist before evaluation."
    )
    with open(TRIAL_ID_PATH) as f:
        content = f.read().strip()
    assert content, f"Trial id file {TRIAL_ID_PATH} must not be empty."


def test_llama_cloud_sdk_installed():
    # The @llamaindex/llama-cloud SDK must be importable via Node's require().
    result = subprocess.run(
        ["node", "-e", "require.resolve('@llamaindex/llama-cloud')"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        "@llamaindex/llama-cloud is not installed in the project. "
        f"stderr: {result.stderr}"
    )
