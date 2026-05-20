import importlib
import os

import pytest

PROJECT_DIR = "/home/user/myproject"
DOCS_DIR = os.path.join(PROJECT_DIR, "docs")
PRODUCT_DOCS_DIR = os.path.join(DOCS_DIR, "product")
FAQ_DOCS_DIR = os.path.join(DOCS_DIR, "faq")


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."


def test_product_docs_directory_exists():
    assert os.path.isdir(PRODUCT_DOCS_DIR), (
        f"Expected product docs directory {PRODUCT_DOCS_DIR} to exist before the task starts."
    )


def test_faq_docs_directory_exists():
    assert os.path.isdir(FAQ_DOCS_DIR), (
        f"Expected FAQ docs directory {FAQ_DOCS_DIR} to exist before the task starts."
    )


def test_product_docs_have_markdown_files():
    files = [f for f in os.listdir(PRODUCT_DOCS_DIR) if f.endswith(".md")]
    assert files, f"Expected at least one .md file in {PRODUCT_DOCS_DIR}."


def test_faq_docs_have_markdown_files():
    files = [f for f in os.listdir(FAQ_DOCS_DIR) if f.endswith(".md")]
    assert files, f"Expected at least one .md file in {FAQ_DOCS_DIR}."


def test_llama_cloud_api_key_env_set():
    assert os.environ.get("LLAMA_CLOUD_API_KEY"), (
        "LLAMA_CLOUD_API_KEY environment variable must be set before the task starts."
    )


def test_trial_id_file_present():
    assert os.path.isfile("/logs/artifacts/trial_id"), (
        "Expected /logs/artifacts/trial_id to be present so the task can scope resources per trial."
    )


@pytest.mark.parametrize(
    "module_name",
    [
        "llama_index",
        "llama_index.core",
        "llama_index.indices.managed.llama_cloud",
        "llama_cloud",
    ],
)
def test_llama_cloud_python_sdk_importable(module_name):
    try:
        importlib.import_module(module_name)
    except ImportError as exc:
        pytest.fail(
            f"Expected Python module '{module_name}' to be importable in the task environment: {exc}"
        )
