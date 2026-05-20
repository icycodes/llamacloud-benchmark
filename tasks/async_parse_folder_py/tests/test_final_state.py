import os
import re

import pytest

PROJECT_DIR = "/home/user/myproject"
INPUT_DIR = os.path.join(PROJECT_DIR, "input_pdfs")
OUTPUT_DIR = os.path.join(PROJECT_DIR, "output_md")
LOG_FILE = os.path.join(PROJECT_DIR, "output.log")
TRIAL_ID_PATH = "/logs/artifacts/trial_id"

EXPECTED_DOCS = [
    ("doc_alpha", "Alpha report sentinel ABC-123"),
    ("doc_beta", "Beta report sentinel BETA-456"),
    ("doc_gamma", "Gamma report sentinel GAMMA-789"),
]


def _read_trial_id():
    with open(TRIAL_ID_PATH, "r", encoding="utf-8") as fh:
        return fh.read().strip()


def test_script_exists():
    script_path = os.path.join(PROJECT_DIR, "parse_folder.py")
    assert os.path.isfile(script_path), (
        f"Expected agent-authored script {script_path} is missing."
    )


def test_output_directory_created():
    assert os.path.isdir(OUTPUT_DIR), (
        f"Output directory {OUTPUT_DIR} was not created by the script."
    )


@pytest.mark.parametrize("base,sentinel", EXPECTED_DOCS)
def test_markdown_output_exists(base, sentinel):
    md_path = os.path.join(OUTPUT_DIR, f"{base}.md")
    assert os.path.isfile(md_path), (
        f"Expected Markdown output {md_path} is missing."
    )
    assert os.path.getsize(md_path) > 0, (
        f"Markdown output {md_path} exists but is empty."
    )


@pytest.mark.parametrize("base,sentinel", EXPECTED_DOCS)
def test_markdown_contains_sentinel(base, sentinel):
    md_path = os.path.join(OUTPUT_DIR, f"{base}.md")
    with open(md_path, "r", encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    # LlamaParse may slightly reformat whitespace, so collapse whitespace before checking.
    collapsed = re.sub(r"\s+", " ", text)
    assert sentinel in collapsed, (
        f"Sentinel text {sentinel!r} not found in parsed Markdown {md_path}."
    )


def test_log_file_exists():
    assert os.path.isfile(LOG_FILE), f"Expected log file {LOG_FILE} is missing."


@pytest.mark.parametrize("base,_sentinel", EXPECTED_DOCS)
def test_log_line_for_each_document(base, _sentinel):
    trial_id = _read_trial_id()
    expected_line = (
        f"Parsed: {base}.pdf -> output_md/{base}.md (trial_id={trial_id})"
    )
    with open(LOG_FILE, "r", encoding="utf-8") as fh:
        lines = [line.rstrip("\n") for line in fh.readlines()]
    assert expected_line in lines, (
        f"Expected log line {expected_line!r} not found in {LOG_FILE}. "
        f"Actual lines: {lines}"
    )
