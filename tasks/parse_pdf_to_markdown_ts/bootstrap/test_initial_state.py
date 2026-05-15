import os
import shutil

import pytest

PROJECT_DIR = "/home/user/myproject"
SAMPLE_PDF = os.path.join(PROJECT_DIR, "sample.pdf")
PACKAGE_JSON = os.path.join(PROJECT_DIR, "package.json")
NODE_MODULES = os.path.join(PROJECT_DIR, "node_modules")
LLAMA_CLOUD_PKG = os.path.join(NODE_MODULES, "@llamaindex", "llama-cloud", "package.json")
TSX_BIN = os.path.join(NODE_MODULES, ".bin", "tsx")
TRIAL_ID_PATH = "/logs/artifacts/trial_id"


def test_node_binary_available():
    """Node.js must be installed in the task environment for the TypeScript runtime."""
    assert shutil.which("node") is not None, (
        "`node` binary not found in PATH. Node.js v24 is required to run the TypeScript task."
    )


def test_npx_binary_available():
    """`npx` must be available so the agent can launch `tsx` via `npx tsx`."""
    assert shutil.which("npx") is not None, (
        "`npx` binary not found in PATH. It is required to execute `npx tsx parse_doc.ts`."
    )


def test_project_directory_exists():
    """The project directory specified in the task must exist."""
    assert os.path.isdir(PROJECT_DIR), (
        f"Expected project directory {PROJECT_DIR} to exist before the task starts."
    )


def test_package_json_exists():
    """A Node project (package.json) must already be initialized in the project dir."""
    assert os.path.isfile(PACKAGE_JSON), (
        f"Expected Node package manifest at {PACKAGE_JSON} to be pre-staged so the "
        "TypeScript script can resolve its dependencies."
    )


def test_local_llama_cloud_sdk_installed():
    """The official `@llamaindex/llama-cloud` Node SDK must be installed in the project."""
    assert os.path.isfile(LLAMA_CLOUD_PKG), (
        f"Expected `@llamaindex/llama-cloud` SDK to be installed at "
        f"{NODE_MODULES}/@llamaindex/llama-cloud (missing {LLAMA_CLOUD_PKG})."
    )


def test_local_tsx_runner_installed():
    """The `tsx` TypeScript runner must be installed locally for `npx tsx` to work offline."""
    assert os.path.isfile(TSX_BIN), (
        f"Expected the `tsx` TypeScript runner binary at {TSX_BIN}, but it was not found."
    )


def test_sample_pdf_exists():
    """The pre-staged sample PDF that the agent will parse must exist."""
    assert os.path.isfile(SAMPLE_PDF), (
        f"Expected sample PDF at {SAMPLE_PDF} to be present before the task starts."
    )
    assert os.path.getsize(SAMPLE_PDF) > 0, (
        f"Sample PDF at {SAMPLE_PDF} is empty; it must contain real PDF content."
    )


def test_sample_pdf_has_pdf_magic_header():
    """sample.pdf should start with the standard `%PDF-` magic header."""
    with open(SAMPLE_PDF, "rb") as f:
        head = f.read(5)
    assert head == b"%PDF-", (
        f"Expected {SAMPLE_PDF} to start with the PDF magic header `%PDF-`, "
        f"but got: {head!r}."
    )


def test_llama_cloud_api_key_env_var_is_set():
    """The LlamaCloud API key environment variable must be available to the task."""
    value = os.environ.get("LLAMA_CLOUD_API_KEY")
    assert value, (
        "Environment variable `LLAMA_CLOUD_API_KEY` is not set; "
        "LlamaParse cannot authenticate without it."
    )


def test_trial_id_file_exists():
    """The trial_id file used for parallel-run isolation must be present."""
    assert os.path.isfile(TRIAL_ID_PATH), (
        f"Expected trial_id file at {TRIAL_ID_PATH} to exist before the task starts."
    )
    with open(TRIAL_ID_PATH, "r", encoding="utf-8") as f:
        content = f.read().strip()
    assert content, f"trial_id file at {TRIAL_ID_PATH} is empty."
