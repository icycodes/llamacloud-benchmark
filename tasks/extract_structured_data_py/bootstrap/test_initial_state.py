import os
import shutil
import subprocess

PROJECT_DIR = "/home/user/myproject"
INPUT_FILE = os.path.join(PROJECT_DIR, "candidate.txt")


def test_python3_available():
    assert shutil.which("python3") is not None, "python3 binary not found in PATH."


def test_llama_cloud_sdk_installed():
    """The llama-cloud Python SDK must be installed in the environment."""
    result = subprocess.run(
        ["python3", "-c", "import llama_cloud; print(llama_cloud.__name__)"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Failed to import the 'llama_cloud' package. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )


def test_pydantic_installed():
    """The pydantic package must be available for defining the schema."""
    result = subprocess.run(
        ["python3", "-c", "import pydantic; print(pydantic.VERSION)"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Failed to import the 'pydantic' package. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Expected project directory at {PROJECT_DIR}, but it does not exist."
    )


def test_candidate_text_file_exists():
    assert os.path.isfile(INPUT_FILE), (
        f"Expected input file at {INPUT_FILE}, but it does not exist."
    )


def test_candidate_text_file_contains_known_fields():
    """The provided candidate.txt must contain the known seed fields used by the verifier."""
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    assert "Alice Johnson" in content, (
        f"Expected 'Alice Johnson' to appear in {INPUT_FILE}, got: {content!r}"
    )
    assert "alice.johnson@example.com" in content, (
        f"Expected email 'alice.johnson@example.com' to appear in {INPUT_FILE}, got: {content!r}"
    )
    for skill in ("Python", "Machine Learning", "Docker", "Kubernetes"):
        assert skill in content, (
            f"Expected skill {skill!r} to appear in {INPUT_FILE}, got: {content!r}"
        )


def test_llama_cloud_api_key_env_set():
    """The LLAMA_CLOUD_API_KEY environment variable must be set for the task to call LlamaExtract."""
    assert os.environ.get("LLAMA_CLOUD_API_KEY"), (
        "LLAMA_CLOUD_API_KEY environment variable is not set in the task environment."
    )
