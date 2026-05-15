import os
import shutil
import subprocess

PROJECT_DIR = "/home/user/myproject"


def test_python3_available():
    assert shutil.which("python3") is not None, "python3 binary not found in PATH."


def test_llama_cloud_package_installed():
    """Verify the llama-cloud Python SDK is importable."""
    result = subprocess.run(
        [
            "python3",
            "-c",
            "from llama_cloud import LlamaCloud; print('ok')",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        "Failed to import LlamaCloud from llama_cloud: "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "ok" in result.stdout, (
        "Expected 'ok' to be printed when importing LlamaCloud, "
        f"got stdout={result.stdout!r}"
    )


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_llama_cloud_api_key_env_set():
    assert os.environ.get("LLAMA_CLOUD_API_KEY"), (
        "LLAMA_CLOUD_API_KEY environment variable is not set."
    )
