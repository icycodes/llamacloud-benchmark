import os
import shutil
import subprocess

PROJECT_DIR = "/home/user/index_task_ts"
DATA_DIR = os.path.join(PROJECT_DIR, "data")
FACTS_FILE = os.path.join(DATA_DIR, "facts.txt")
HISTORY_FILE = os.path.join(DATA_DIR, "history.txt")


def test_node_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."


def test_npx_available():
    assert shutil.which("npx") is not None, "npx binary not found in PATH."


def test_tsx_available():
    """tsx must be globally available for `npx tsx build_index.ts` execution."""
    result = subprocess.run(
        ["npx", "--no-install", "tsx", "--version"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Failed to invoke 'npx tsx --version': stdout={result.stdout!r} stderr={result.stderr!r}"
    )


def test_llama_cloud_services_ts_package_installed():
    """The llama-cloud-services TypeScript framework package must be globally
    resolvable so the executor can import LlamaCloudIndex from inside the
    project directory."""
    result = subprocess.run(
        ["node", "-e", "require.resolve('llama-cloud-services')"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        "llama-cloud-services could not be resolved from "
        f"{PROJECT_DIR}: stdout={result.stdout!r} stderr={result.stderr!r}"
    )


def test_llamaindex_ts_package_installed():
    """The llamaindex TypeScript framework package must be globally resolvable
    so the executor can import the Document class from inside the project
    directory."""
    result = subprocess.run(
        ["node", "-e", "require.resolve('llamaindex')"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        "llamaindex could not be resolved from "
        f"{PROJECT_DIR}: stdout={result.stdout!r} stderr={result.stderr!r}"
    )


def test_python3_available_for_verifier_sdk_checks():
    """Python 3 is required by the verifier to call the LlamaCloud Python SDK."""
    assert shutil.which("python3") is not None, "python3 binary not found in PATH."


def test_llama_cloud_python_sdk_importable():
    """The LlamaCloud Python SDK must already be installed so the verifier can
    confirm that the TypeScript-created managed index actually exists on the
    LlamaCloud platform."""
    result = subprocess.run(
        ["python3", "-c", "import llama_cloud"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Failed to import llama_cloud: stdout={result.stdout!r} stderr={result.stderr!r}"
    )


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_data_dir_exists():
    assert os.path.isdir(DATA_DIR), (
        f"Seed data directory {DATA_DIR} does not exist."
    )


def test_facts_file_exists_with_expected_content():
    assert os.path.isfile(FACTS_FILE), (
        f"Expected pre-seeded {FACTS_FILE} was not found."
    )
    with open(FACTS_FILE, "r", encoding="utf-8") as fp:
        content = fp.read()
    assert "The capital of Atlantis is Pochi City." in content, (
        f"{FACTS_FILE} is missing the expected seeded sentence about the capital."
    )


def test_history_file_exists_with_expected_content():
    assert os.path.isfile(HISTORY_FILE), (
        f"Expected pre-seeded {HISTORY_FILE} was not found."
    )
    with open(HISTORY_FILE, "r", encoding="utf-8") as fp:
        content = fp.read()
    assert "Atlantis was founded in the year 1042" in content, (
        f"{HISTORY_FILE} is missing the expected seeded sentence about Atlantis history."
    )


def test_trial_id_file_exists():
    """The harbor trial_id artifact must exist before the task starts."""
    assert os.path.isfile("/logs/artifacts/trial_id"), (
        "/logs/artifacts/trial_id is missing; cannot scope LlamaCloud resources per trial."
    )


def test_build_script_not_pre_created():
    """The executor must create build_index.ts; it must not exist initially."""
    build_ts = os.path.join(PROJECT_DIR, "build_index.ts")
    assert not os.path.exists(build_ts), (
        f"{build_ts} should not exist at task start; the executor must create it."
    )


def test_output_log_not_pre_created():
    """The executor must create output.log; it must not exist initially."""
    output_log = os.path.join(PROJECT_DIR, "output.log")
    assert not os.path.exists(output_log), (
        f"{output_log} should not exist at task start; the executor must create it."
    )
