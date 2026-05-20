import os
import shutil


PROJECT_DIR = "/home/user/myproject"
FIXTURE_PDF = os.path.join(PROJECT_DIR, "fixtures", "sample.pdf")


def test_node_binary_available():
    assert shutil.which("node") is not None, (
        "node binary not found in PATH; the TypeScript SDK requires Node.js."
    )


def test_npx_binary_available():
    assert shutil.which("npx") is not None, (
        "npx binary not found in PATH; the task entrypoint uses `npx tsx`."
    )


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_fixture_pdf_exists():
    assert os.path.isfile(FIXTURE_PDF), (
        f"Fixture PDF {FIXTURE_PDF} does not exist; verification depends on it."
    )


def test_fixture_pdf_non_empty():
    assert os.path.getsize(FIXTURE_PDF) > 0, (
        f"Fixture PDF {FIXTURE_PDF} is empty; verification cannot proceed."
    )


def test_llama_cloud_api_key_set():
    assert os.environ.get("LLAMA_CLOUD_API_KEY"), (
        "LLAMA_CLOUD_API_KEY environment variable is not set; "
        "the task requires it to call the real LlamaCloud API."
    )
