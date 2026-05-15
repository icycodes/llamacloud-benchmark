import importlib
import os

import pytest

PROJECT_DIR = "/home/user/parse_json_task"
SAMPLE_PDF = os.path.join(PROJECT_DIR, "sample.pdf")
MARKER_BY_PAGE = {
    1: ("JSON-Mode-Page-One", "500,000"),
    2: ("JSON-Mode-Page-Two", "750,000"),
    3: ("JSON-Mode-Page-Three", "1,000,000"),
}


def test_llama_parse_sdk_importable():
    """At least one of the official LlamaParse SDK packages must be importable."""
    found = None
    for candidate in ("llama_cloud_services", "llama_parse"):
        try:
            importlib.import_module(candidate)
            found = candidate
            break
        except Exception:
            continue
    assert found is not None, (
        "Expected one of the LlamaParse SDK packages "
        "(`llama_cloud_services` or `llama_parse`) to be importable, but neither was."
    )


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Expected project directory {PROJECT_DIR} to exist before the task starts."
    )


def test_sample_pdf_exists_and_non_empty():
    assert os.path.isfile(SAMPLE_PDF), (
        f"Expected seeded source PDF at {SAMPLE_PDF} to exist before the task starts."
    )
    assert os.path.getsize(SAMPLE_PDF) > 0, (
        f"Seeded PDF {SAMPLE_PDF} must be non-empty."
    )


def test_sample_pdf_contains_all_three_page_markers_and_amounts():
    """The seeded PDF must contain the marker phrase and quarterly revenue
    value for every one of its three pages so the executor's JSON-mode parse
    output can be deterministically verified."""
    pypdf = pytest.importorskip("pypdf")
    reader = pypdf.PdfReader(SAMPLE_PDF)
    assert len(reader.pages) == 3, (
        f"Seeded PDF must have exactly 3 pages, but it has {len(reader.pages)}."
    )
    all_text = "\n".join(page.extract_text() or "" for page in reader.pages)
    for page_number, (marker, amount) in MARKER_BY_PAGE.items():
        assert marker in all_text, (
            f"Expected the seeded PDF to contain marker '{marker}' for page "
            f"{page_number}, but it was missing."
        )
        assert amount in all_text, (
            f"Expected the seeded PDF to contain revenue amount '{amount}' for "
            f"page {page_number}, but it was missing."
        )


def test_trial_id_artifact_available():
    """The /logs/artifacts/trial_id file must be available so the executor can
    embed the trial id in its log output and JSON manifest."""
    path = "/logs/artifacts/trial_id"
    assert os.path.isfile(path), (
        f"Expected trial id artifact at {path}, but the file is missing."
    )
    with open(path, "r", encoding="utf-8") as fp:
        value = fp.read().strip()
    assert value, f"Trial id artifact at {path} must not be empty."
