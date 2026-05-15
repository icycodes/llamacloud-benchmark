import importlib
import os

import pytest

PROJECT_DIR = "/home/user/myproject"
DOCS_ASTRO = os.path.join(PROJECT_DIR, "docs_astronomy")
DOCS_COOK = os.path.join(PROJECT_DIR, "docs_cooking")
TRIAL_ID_PATH = "/logs/artifacts/trial_id"


def test_llama_cloud_services_importable():
    """The `llama_cloud_services` SDK must be importable in the task environment."""
    try:
        module = importlib.import_module("llama_cloud_services")
    except ImportError as exc:
        pytest.fail(
            "`llama_cloud_services` is not importable: "
            f"{exc}. It is required to use LlamaCloudIndex and "
            "LlamaCloudCompositeRetriever in this task."
        )
    assert module is not None, (
        "Imported `llama_cloud_services` module is None."
    )


def test_llama_cloud_module_importable():
    """The `llama_cloud` package (for `CompositeRetrievalMode`) must be importable."""
    try:
        module = importlib.import_module("llama_cloud")
    except ImportError as exc:
        pytest.fail(
            "`llama_cloud` is not importable: "
            f"{exc}. It is required for the `CompositeRetrievalMode` enum."
        )
    assert module is not None, "Imported `llama_cloud` module is None."


def test_managed_llama_cloud_index_importable():
    """The managed LlamaCloud index module must be importable as a fallback alias."""
    try:
        module = importlib.import_module(
            "llama_index.indices.managed.llama_cloud"
        )
    except ImportError as exc:
        pytest.fail(
            "`llama_index.indices.managed.llama_cloud` is not importable: "
            f"{exc}. It is required as the managed LlamaCloud SDK."
        )
    assert module is not None, (
        "Imported `llama_index.indices.managed.llama_cloud` module is None."
    )


def test_llama_index_core_importable():
    """`llama_index.core` (for SimpleDirectoryReader) must be importable."""
    try:
        module = importlib.import_module("llama_index.core")
    except ImportError as exc:
        pytest.fail(
            f"`llama_index.core` is not importable: {exc}. It is required for "
            "loading local documents with SimpleDirectoryReader."
        )
    assert module is not None, "Imported `llama_index.core` module is None."


def test_project_directory_exists():
    """The project directory specified in the task must exist."""
    assert os.path.isdir(PROJECT_DIR), (
        f"Expected project directory {PROJECT_DIR} to exist before the task starts."
    )


def test_docs_astronomy_directory_exists_and_non_empty():
    """The pre-staged astronomy docs directory must exist and be non-empty."""
    assert os.path.isdir(DOCS_ASTRO), (
        f"Expected docs directory {DOCS_ASTRO} to exist before the task starts."
    )
    entries = [
        e
        for e in os.listdir(DOCS_ASTRO)
        if os.path.isfile(os.path.join(DOCS_ASTRO, e))
    ]
    assert len(entries) > 0, (
        f"Expected at least one document file in {DOCS_ASTRO}, found none."
    )


def test_docs_cooking_directory_exists_and_non_empty():
    """The pre-staged cooking docs directory must exist and be non-empty."""
    assert os.path.isdir(DOCS_COOK), (
        f"Expected docs directory {DOCS_COOK} to exist before the task starts."
    )
    entries = [
        e
        for e in os.listdir(DOCS_COOK)
        if os.path.isfile(os.path.join(DOCS_COOK, e))
    ]
    assert len(entries) > 0, (
        f"Expected at least one document file in {DOCS_COOK}, found none."
    )


def test_docs_astronomy_contains_project_aurora_text():
    """At least one astronomy doc must mention 'Project Aurora' so the retriever has a target."""
    found = False
    for name in os.listdir(DOCS_ASTRO):
        path = os.path.join(DOCS_ASTRO, name)
        if not os.path.isfile(path):
            continue
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except OSError:
            continue
        if "project aurora" in content.lower():
            found = True
            break
    assert found, (
        f"Expected at least one file under {DOCS_ASTRO} to mention 'Project Aurora'."
    )


def test_docs_cooking_contains_honey_and_lemon_text():
    """At least one cooking doc must mention both 'honey' and 'lemon'."""
    found = False
    for name in os.listdir(DOCS_COOK):
        path = os.path.join(DOCS_COOK, name)
        if not os.path.isfile(path):
            continue
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read().lower()
        except OSError:
            continue
        if "honey" in content and "lemon" in content:
            found = True
            break
    assert found, (
        f"Expected at least one file under {DOCS_COOK} to mention both 'honey' and 'lemon'."
    )


def test_llama_cloud_api_key_env_var_is_set():
    """The LlamaCloud API key environment variable must be available to the task."""
    value = os.environ.get("LLAMA_CLOUD_API_KEY")
    assert value, (
        "Environment variable `LLAMA_CLOUD_API_KEY` is not set; the managed "
        "LlamaCloud SDK cannot authenticate without it."
    )


def test_trial_id_file_exists():
    """The trial_id file used for parallel-run isolation must be present."""
    assert os.path.isfile(TRIAL_ID_PATH), (
        f"Expected trial_id file at {TRIAL_ID_PATH} to exist before the task starts."
    )
    with open(TRIAL_ID_PATH, "r", encoding="utf-8") as f:
        content = f.read().strip()
    assert content, f"trial_id file at {TRIAL_ID_PATH} is empty."
