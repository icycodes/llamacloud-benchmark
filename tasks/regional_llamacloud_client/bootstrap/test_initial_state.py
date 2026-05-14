import os
import subprocess

PROJECT_DIR = "/home/user/llamacloud_region"


def test_python3_available():
    import shutil
    assert shutil.which("python3") is not None, "python3 binary not found in PATH."


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Expected project directory {PROJECT_DIR} to exist in the initial state."
    )


def test_llama_cloud_sdk_importable():
    """The llama_cloud SDK must be installed so the agent can import LlamaCloud."""
    result = subprocess.run(
        ["python3", "-c", "from llama_cloud.client import LlamaCloud; print('ok')"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Expected `from llama_cloud.client import LlamaCloud` to succeed but got: "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "ok" in result.stdout, (
        f"Expected import smoke test to print 'ok'; got stdout={result.stdout!r}"
    )
