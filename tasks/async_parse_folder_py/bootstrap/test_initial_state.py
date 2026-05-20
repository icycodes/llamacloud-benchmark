import importlib
import os

import pytest

PROJECT_DIR = "/home/user/myproject"
INPUT_DIR = os.path.join(PROJECT_DIR, "input_pdfs")
EXPECTED_PDFS = ["doc_alpha.pdf", "doc_beta.pdf", "doc_gamma.pdf"]


def test_llama_parse_importable():
    try:
        importlib.import_module("llama_parse")
    except ImportError as exc:  # pragma: no cover - failure path
        pytest.fail(f"llama_parse package is not importable: {exc}")


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."


def test_input_pdfs_dir_exists():
    assert os.path.isdir(INPUT_DIR), f"Input PDF directory {INPUT_DIR} does not exist."


@pytest.mark.parametrize("pdf_name", EXPECTED_PDFS)
def test_input_pdf_present(pdf_name):
    pdf_path = os.path.join(INPUT_DIR, pdf_name)
    assert os.path.isfile(pdf_path), f"Expected sample input PDF {pdf_path} is missing."
    assert os.path.getsize(pdf_path) > 0, f"Sample input PDF {pdf_path} is empty."


def test_llama_cloud_api_key_env_present():
    value = os.environ.get("LLAMA_CLOUD_API_KEY")
    assert value, "LLAMA_CLOUD_API_KEY environment variable must be set in the task environment."


def test_trial_id_artifact_present():
    trial_path = "/logs/artifacts/trial_id"
    assert os.path.isfile(trial_path), f"trial_id artifact {trial_path} must exist for the task to run."
