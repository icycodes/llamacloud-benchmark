import os
import shutil
import subprocess

PROJECT_DIR = "/home/user/myproject"
INPUT_FILE = os.path.join(PROJECT_DIR, "document.txt")


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


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Expected project directory at {PROJECT_DIR}, but it does not exist."
    )


def test_document_text_file_exists():
    assert os.path.isfile(INPUT_FILE), (
        f"Expected input file at {INPUT_FILE}, but it does not exist."
    )


def test_document_text_file_contains_invoice_fields():
    """The provided document.txt must contain the known invoice fields used by the verifier."""
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    for fragment in (
        "INVOICE #INV-2024-001",
        "Invoice Date: 2024-03-15",
        "Bill To: Acme Corp.",
        "Consulting Services",
        "Software License",
        "Total: $2,970.00",
    ):
        assert fragment in content, (
            f"Expected fragment {fragment!r} to appear in {INPUT_FILE}, got: {content!r}"
        )


def test_llama_cloud_api_key_env_set():
    """The LLAMA_CLOUD_API_KEY environment variable must be set for the task to call LlamaClassify."""
    assert os.environ.get("LLAMA_CLOUD_API_KEY"), (
        "LLAMA_CLOUD_API_KEY environment variable is not set in the task environment."
    )
