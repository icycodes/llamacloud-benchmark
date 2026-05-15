import json
import os
import shutil
import subprocess

PROJECT_DIR = "/home/user/myproject"
SAMPLE_PDF = "/home/user/myproject/sample.pdf"
PACKAGE_JSON = "/home/user/myproject/package.json"
NODE_MODULES = "/home/user/myproject/node_modules"
LLAMA_CLOUD_PKG = "/home/user/myproject/node_modules/@llamaindex/llama-cloud/package.json"
TSX_BIN = "/home/user/myproject/node_modules/.bin/tsx"


def test_node_available():
    assert shutil.which("node") is not None, \
        "node binary not found in PATH; Node.js is required to run the LlamaParse TypeScript CLI."


def test_npm_available():
    assert shutil.which("npm") is not None, \
        "npm binary not found in PATH; npm is required for the Node.js project workflow."


def test_npx_available():
    assert shutil.which("npx") is not None, \
        "npx binary not found in PATH; the task uses `npx tsx` to run the TypeScript CLI."


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), \
        f"Project directory {PROJECT_DIR} does not exist; it must be pre-created in the environment."


def test_sample_pdf_exists():
    assert os.path.isfile(SAMPLE_PDF), \
        f"Sample PDF {SAMPLE_PDF} is missing; the initial environment must provide it for the task."


def test_sample_pdf_is_nonempty():
    size = os.path.getsize(SAMPLE_PDF)
    assert size > 0, f"Sample PDF {SAMPLE_PDF} is empty (size={size}); it must contain a real PDF document."


def test_sample_pdf_has_pdf_magic_bytes():
    with open(SAMPLE_PDF, "rb") as fh:
        header = fh.read(5)
    assert header.startswith(b"%PDF-"), \
        f"Sample PDF {SAMPLE_PDF} does not begin with the '%PDF-' magic bytes; it is not a valid PDF."


def test_package_json_exists():
    assert os.path.isfile(PACKAGE_JSON), \
        f"Expected an initialized Node.js project with {PACKAGE_JSON}, but the file does not exist."


def test_package_json_declares_esm_module_type():
    with open(PACKAGE_JSON, "r", encoding="utf-8") as fh:
        pkg = json.load(fh)
    assert pkg.get("type") == "module", \
        f"Expected package.json to declare `\"type\": \"module\"` so that top-level await works with tsx; got: {pkg.get('type')!r}"


def test_node_modules_directory_exists():
    assert os.path.isdir(NODE_MODULES), \
        f"Expected pre-installed node_modules at {NODE_MODULES}; npm dependencies must be installed in the initial environment."


def test_llama_cloud_sdk_installed():
    assert os.path.isfile(LLAMA_CLOUD_PKG), \
        (f"Expected the @llamaindex/llama-cloud TypeScript SDK to be pre-installed at "
         f"{LLAMA_CLOUD_PKG}, but the package.json is missing.")


def test_tsx_binary_installed():
    assert os.path.isfile(TSX_BIN), \
        f"Expected the tsx binary to be installed at {TSX_BIN}, but it is missing."


def test_tsx_executable_runs():
    result = subprocess.run(
        ["npx", "tsx", "--version"],
        capture_output=True, text=True, cwd=PROJECT_DIR,
    )
    assert result.returncode == 0, \
        f"`npx tsx --version` failed in {PROJECT_DIR}. stderr: {result.stderr}"


def test_llama_cloud_api_key_present_in_env():
    assert os.environ.get("LLAMA_CLOUD_API_KEY"), \
        "LLAMA_CLOUD_API_KEY environment variable must be set so the SDK can authenticate against LlamaCloud."
