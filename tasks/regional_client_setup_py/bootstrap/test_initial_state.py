import importlib
import os


PROJECT_DIR = "/home/user/myproject"


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_llama_cloud_services_importable():
    try:
        importlib.import_module("llama_cloud_services")
    except ImportError as exc:  # pragma: no cover - assertion provides message
        raise AssertionError(
            "The 'llama_cloud_services' package must be importable in the task "
            f"environment (got ImportError: {exc})."
        )


def test_llama_parse_importable():
    module = importlib.import_module("llama_cloud_services")
    assert hasattr(module, "LlamaParse"), (
        "Expected 'LlamaParse' to be exported from 'llama_cloud_services'."
    )


def test_eu_base_url_constant_available():
    module = importlib.import_module("llama_cloud_services")
    assert hasattr(module, "EU_BASE_URL"), (
        "Expected 'EU_BASE_URL' constant to be exported from "
        "'llama_cloud_services'."
    )
