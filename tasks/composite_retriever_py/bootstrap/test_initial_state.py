import os
import shutil
import subprocess

PROJECT_DIR = "/home/user/myproject"
PRODUCTS_DIR = os.path.join(PROJECT_DIR, "products")
SUPPORT_DIR = os.path.join(PROJECT_DIR, "support")
PRODUCTS_FILE = os.path.join(PRODUCTS_DIR, "widget_specs.txt")
SUPPORT_FILE = os.path.join(SUPPORT_DIR, "faq.txt")


def test_python3_available():
    assert shutil.which("python3") is not None, "python3 binary not found in PATH."


def test_llama_index_managed_package_installed():
    """Verify LlamaCloudIndex is importable from the managed integration."""
    result = subprocess.run(
        [
            "python3",
            "-c",
            "from llama_index.indices.managed.llama_cloud import LlamaCloudIndex; print('ok')",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        "Failed to import LlamaCloudIndex from "
        "llama_index.indices.managed.llama_cloud: "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "ok" in result.stdout, (
        "Expected 'ok' to be printed when importing LlamaCloudIndex, "
        f"got stdout={result.stdout!r}"
    )


def test_llama_cloud_composite_retriever_available():
    """Verify LlamaCloudCompositeRetriever is importable from the managed integration."""
    result = subprocess.run(
        [
            "python3",
            "-c",
            "from llama_index.indices.managed.llama_cloud import LlamaCloudCompositeRetriever; print('ok')",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        "Failed to import LlamaCloudCompositeRetriever from "
        "llama_index.indices.managed.llama_cloud: "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "ok" in result.stdout, (
        "Expected 'ok' to be printed when importing LlamaCloudCompositeRetriever, "
        f"got stdout={result.stdout!r}"
    )


def test_composite_retrieval_mode_available():
    """Verify CompositeRetrievalMode is importable from llama_cloud."""
    result = subprocess.run(
        [
            "python3",
            "-c",
            "from llama_cloud import CompositeRetrievalMode; print('ok')",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        "Failed to import CompositeRetrievalMode from llama_cloud: "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "ok" in result.stdout, (
        "Expected 'ok' to be printed when importing CompositeRetrievalMode, "
        f"got stdout={result.stdout!r}"
    )


def test_simple_directory_reader_available():
    """Verify SimpleDirectoryReader is importable from llama_index.core."""
    result = subprocess.run(
        [
            "python3",
            "-c",
            "from llama_index.core import SimpleDirectoryReader; print('ok')",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        "Failed to import SimpleDirectoryReader from llama_index.core: "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "ok" in result.stdout, (
        "Expected 'ok' to be printed when importing SimpleDirectoryReader, "
        f"got stdout={result.stdout!r}"
    )


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_products_directory_exists():
    assert os.path.isdir(PRODUCTS_DIR), (
        f"Initial products directory {PRODUCTS_DIR} does not exist."
    )


def test_support_directory_exists():
    assert os.path.isdir(SUPPORT_DIR), (
        f"Initial support directory {SUPPORT_DIR} does not exist."
    )


def test_products_file_exists():
    assert os.path.isfile(PRODUCTS_FILE), (
        f"Initial sample document {PRODUCTS_FILE} does not exist."
    )


def test_support_file_exists():
    assert os.path.isfile(SUPPORT_FILE), (
        f"Initial sample document {SUPPORT_FILE} does not exist."
    )


def test_products_content_present():
    """The initial products document must mention Model X100 and 175 degrees."""
    with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    assert "Model X100" in content, (
        "Initial widget_specs.txt does not mention 'Model X100'."
    )
    assert "175" in content, (
        "Initial widget_specs.txt does not mention the operating temperature '175'."
    )


def test_support_content_present():
    """The initial support document must contain FAQ entries."""
    with open(SUPPORT_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    assert "Q:" in content, (
        "Initial faq.txt does not contain any question lines ('Q:')."
    )
    assert "warranty" in content.lower(), (
        "Initial faq.txt does not mention 'warranty'."
    )


def test_trial_id_file_present():
    """The harness must provide /logs/artifacts/trial_id before the task starts."""
    trial_id_path = "/logs/artifacts/trial_id"
    assert os.path.isfile(trial_id_path), (
        f"Expected trial_id file at {trial_id_path}; it is required by the task."
    )
    with open(trial_id_path, "r", encoding="utf-8") as f:
        trial_id = f.read().strip()
    assert trial_id, (
        f"trial_id file {trial_id_path} is empty; the task requires a non-empty trial_id."
    )


def test_llama_cloud_api_key_env_set():
    assert os.environ.get("LLAMA_CLOUD_API_KEY"), (
        "LLAMA_CLOUD_API_KEY environment variable is not set."
    )
