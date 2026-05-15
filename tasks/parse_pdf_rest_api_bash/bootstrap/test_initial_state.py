import os
import shutil

PROJECT_DIR = "/home/user/myproject"
SAMPLE_PDF = os.path.join(PROJECT_DIR, "sample.pdf")


def test_bash_available():
    assert shutil.which("bash") is not None, \
        "bash binary not found in PATH; bash is required to run parse.sh."


def test_curl_available():
    assert shutil.which("curl") is not None, \
        "curl binary not found in PATH; curl is required to invoke the LlamaCloud REST API."


def test_jq_available():
    assert shutil.which("jq") is not None, \
        "jq binary not found in PATH; jq is required to parse JSON responses from the LlamaCloud REST API."


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), \
        f"Project directory {PROJECT_DIR} does not exist; it must be pre-created in the environment."


def test_sample_pdf_exists():
    assert os.path.isfile(SAMPLE_PDF), \
        f"Sample PDF {SAMPLE_PDF} is missing; the initial environment must provide it for the task."


def test_sample_pdf_is_nonempty():
    size = os.path.getsize(SAMPLE_PDF)
    assert size > 0, \
        f"Sample PDF {SAMPLE_PDF} is empty (size={size}); it must contain a real PDF document."


def test_sample_pdf_has_pdf_magic_bytes():
    with open(SAMPLE_PDF, "rb") as fh:
        header = fh.read(5)
    assert header.startswith(b"%PDF-"), \
        f"Sample PDF {SAMPLE_PDF} does not begin with the '%PDF-' magic bytes; it is not a valid PDF."


def test_llama_cloud_api_key_present_in_env():
    assert os.environ.get("LLAMA_CLOUD_API_KEY"), \
        "LLAMA_CLOUD_API_KEY environment variable must be set so the script can authenticate against the LlamaCloud REST API."
