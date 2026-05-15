import importlib
import os

import pytest

PROJECT_DIR = "/home/user/myproject"
DOCS_INITIAL_DIR = os.path.join(PROJECT_DIR, "docs_initial")
DOCS_NEW_DIR = os.path.join(PROJECT_DIR, "docs_new")
TRIAL_ID_PATH = "/logs/artifacts/trial_id"


def test_llama_cloud_managed_index_importable():
    """The managed LlamaCloud index SDK must be importable in the task environment."""
    try:
        module = importlib.import_module(
            "llama_index.indices.managed.llama_cloud"
        )
    except ImportError as exc:
        pytest.fail(
            "`llama_index.indices.managed.llama_cloud` is not importable: "
            f"{exc}. The managed LlamaCloud SDK must be available in the task "
            "environment."
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


def test_docs_initial_directory_exists_and_non_empty():
    """The pre-staged docs_initial directory must exist and be non-empty."""
    assert os.path.isdir(DOCS_INITIAL_DIR), (
        f"Expected docs_initial directory {DOCS_INITIAL_DIR} to exist before the task starts."
    )
    entries = [
        e
        for e in os.listdir(DOCS_INITIAL_DIR)
        if os.path.isfile(os.path.join(DOCS_INITIAL_DIR, e))
    ]
    assert len(entries) >= 1, (
        f"Expected at least one file in {DOCS_INITIAL_DIR}, found none."
    )


def test_docs_new_directory_exists_and_non_empty():
    """The pre-staged docs_new directory must exist and be non-empty."""
    assert os.path.isdir(DOCS_NEW_DIR), (
        f"Expected docs_new directory {DOCS_NEW_DIR} to exist before the task starts."
    )
    entries = [
        e
        for e in os.listdir(DOCS_NEW_DIR)
        if os.path.isfile(os.path.join(DOCS_NEW_DIR, e))
    ]
    assert len(entries) >= 1, (
        f"Expected at least one file in {DOCS_NEW_DIR}, found none."
    )


def test_docs_initial_contains_project_aurora_text():
    """The pre-staged initial corpus must mention 'Project Aurora' so the initial-build retriever has a target."""
    found = False
    for name in os.listdir(DOCS_INITIAL_DIR):
        path = os.path.join(DOCS_INITIAL_DIR, name)
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
        f"Expected at least one file under {DOCS_INITIAL_DIR} to mention 'Project Aurora'."
    )


def test_docs_new_contains_project_borealis_text():
    """The pre-staged new corpus must mention 'Project Borealis' so the incremental-ingestion retriever has a target."""
    found = False
    for name in os.listdir(DOCS_NEW_DIR):
        path = os.path.join(DOCS_NEW_DIR, name)
        if not os.path.isfile(path):
            continue
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except OSError:
            continue
        if "project borealis" in content.lower():
            found = True
            break
    assert found, (
        f"Expected at least one file under {DOCS_NEW_DIR} to mention 'Project Borealis'."
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
