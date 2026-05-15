import os
import shutil
import subprocess

PROJECT_DIR = "/home/user/prompted_parse_task"
SAMPLE_PDF = os.path.join(PROJECT_DIR, "sample.pdf")


def test_python3_available():
    assert shutil.which("python3") is not None, "python3 binary not found in PATH."


def test_llama_cloud_sdk_importable():
    """The official LlamaCloud Python SDK must be installed."""
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


def test_sample_pdf_exists_and_non_empty():
    assert os.path.isfile(SAMPLE_PDF), (
        f"Expected pre-seeded {SAMPLE_PDF} was not found."
    )
    assert os.path.getsize(SAMPLE_PDF) > 0, (
        f"Pre-seeded {SAMPLE_PDF} must be a non-empty PDF file."
    )


def test_trial_id_file_exists():
    """The harbor trial_id artifact must exist before the task starts."""
    assert os.path.isfile("/logs/artifacts/trial_id"), (
        "/logs/artifacts/trial_id is missing; cannot scope per-trial log values."
    )


def test_parse_script_not_pre_created():
    """The executor must create parse_with_prompt.py; it must not exist initially."""
    script_path = os.path.join(PROJECT_DIR, "parse_with_prompt.py")
    assert not os.path.exists(script_path), (
        f"{script_path} should not exist at task start; the executor must create it."
    )


def test_output_files_not_pre_created():
    """The executor must create output.md and output.log; they must not exist initially."""
    for name in ("output.md", "output.log"):
        path = os.path.join(PROJECT_DIR, name)
        assert not os.path.exists(path), (
            f"{path} should not exist at task start; the executor must create it."
        )
