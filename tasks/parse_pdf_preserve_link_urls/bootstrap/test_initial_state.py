import os
import shutil
import subprocess

PROJECT_DIR = "/home/user/links_task"
REFERENCES_PDF = os.path.join(PROJECT_DIR, "references.pdf")
OUTPUT_MD = os.path.join(PROJECT_DIR, "links_output.md")
SCRIPT_PATH = os.path.join(PROJECT_DIR, "parse_with_links.py")


def test_python3_available():
    assert shutil.which("python3") is not None, "python3 binary not found in PATH."


def test_llama_cloud_sdk_installed():
    result = subprocess.run(
        ["python3", "-c", "import llama_cloud; print(llama_cloud.__name__)"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"llama_cloud Python package is not importable. stderr: {result.stderr}"
    )


def test_llama_cloud_client_class_available():
    result = subprocess.run(
        [
            "python3",
            "-c",
            "from llama_cloud import LlamaCloud; print(LlamaCloud.__name__)",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"LlamaCloud client class is not importable from llama_cloud. stderr: {result.stderr}"
    )


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Expected project directory {PROJECT_DIR} to exist before task execution."
    )


def test_references_pdf_exists():
    assert os.path.isfile(REFERENCES_PDF), (
        f"Expected initial PDF file {REFERENCES_PDF} to exist before task execution."
    )


def test_references_pdf_is_nonempty():
    assert os.path.getsize(REFERENCES_PDF) > 0, (
        f"Initial PDF file {REFERENCES_PDF} must be non-empty."
    )


def test_references_pdf_is_valid_pdf():
    with open(REFERENCES_PDF, "rb") as f:
        header = f.read(5)
    assert header.startswith(b"%PDF-"), (
        f"Initial file {REFERENCES_PDF} does not appear to be a valid PDF (missing %PDF- header)."
    )


def test_references_pdf_embeds_expected_urls():
    """The source PDF must embed the two URLs that the verification step later asserts on."""
    with open(REFERENCES_PDF, "rb") as f:
        raw = f.read()
    assert b"https://example.com/docs" in raw, (
        f"Initial PDF {REFERENCES_PDF} must embed the URL 'https://example.com/docs' "
        "as a hyperlink destination so the task is solvable."
    )
    assert b"https://llamaindex.ai" in raw, (
        f"Initial PDF {REFERENCES_PDF} must embed the URL 'https://llamaindex.ai' "
        "as a hyperlink destination so the task is solvable."
    )


def test_output_md_not_yet_created():
    assert not os.path.exists(OUTPUT_MD), (
        f"Output file {OUTPUT_MD} must not exist before the task is executed."
    )


def test_parse_script_not_yet_created():
    assert not os.path.exists(SCRIPT_PATH), (
        f"Script {SCRIPT_PATH} must not exist before the task is executed."
    )


def test_llama_cloud_api_key_env_set():
    value = os.environ.get("LLAMA_CLOUD_API_KEY")
    assert value is not None and value.strip() != "", (
        "LLAMA_CLOUD_API_KEY environment variable must be set for the task environment."
    )
