import importlib
import os

import pytest

PROJECT_DIR = "/home/user/myproject"
DOCS_DIR = os.path.join(PROJECT_DIR, "docs")
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


def test_llama_index_llms_openai_importable():
    """`llama_index.llms.openai` must be importable for query engine synthesis."""
    try:
        module = importlib.import_module("llama_index.llms.openai")
    except ImportError as exc:
        pytest.fail(
            f"`llama_index.llms.openai` is not importable: {exc}. It is required "
            "for response synthesis with OpenAI via LlamaIndex."
        )
    assert module is not None, "Imported `llama_index.llms.openai` module is None."


def test_project_directory_exists():
    """The project directory specified in the task must exist."""
    assert os.path.isdir(PROJECT_DIR), (
        f"Expected project directory {PROJECT_DIR} to exist before the task starts."
    )


def test_docs_directory_exists_and_non_empty():
    """The pre-staged docs directory the agent will index must exist and be non-empty."""
    assert os.path.isdir(DOCS_DIR), (
        f"Expected docs directory {DOCS_DIR} to exist before the task starts."
    )
    entries = [
        e
        for e in os.listdir(DOCS_DIR)
        if os.path.isfile(os.path.join(DOCS_DIR, e))
    ]
    assert len(entries) > 0, (
        f"Expected at least one document file in {DOCS_DIR}, found none."
    )


def test_docs_directory_contains_project_aurora_text():
    """At least one pre-staged document must mention 'Project Aurora' so retrieval has a target."""
    found = False
    for name in os.listdir(DOCS_DIR):
        path = os.path.join(DOCS_DIR, name)
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
        f"Expected at least one file under {DOCS_DIR} to mention 'Project Aurora'."
    )


def test_llama_cloud_api_key_env_var_is_set():
    """The LlamaCloud API key environment variable must be available to the task."""
    value = os.environ.get("LLAMA_CLOUD_API_KEY")
    assert value, (
        "Environment variable `LLAMA_CLOUD_API_KEY` is not set; the managed "
        "LlamaCloud SDK cannot authenticate without it."
    )


def test_openai_api_key_env_var_is_set():
    """The OpenAI API key environment variable must be available to the task."""
    value = os.environ.get("OPENAI_API_KEY")
    assert value, (
        "Environment variable `OPENAI_API_KEY` is not set; the query engine "
        "cannot call OpenAI for response synthesis without it."
    )


def test_trial_id_file_exists():
    """The trial_id file used for parallel-run isolation must be present."""
    assert os.path.isfile(TRIAL_ID_PATH), (
        f"Expected trial_id file at {TRIAL_ID_PATH} to exist before the task starts."
    )
    with open(TRIAL_ID_PATH, "r", encoding="utf-8") as f:
        content = f.read().strip()
    assert content, f"trial_id file at {TRIAL_ID_PATH} is empty."
