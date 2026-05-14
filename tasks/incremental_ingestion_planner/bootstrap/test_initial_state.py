import hashlib
import importlib
import json
import os
import shutil

import pytest

PROJECT_DIR = "/home/user/sync_planner"
INPUTS_DIR = os.path.join(PROJECT_DIR, "inputs")
REPORT_MD = os.path.join(INPUTS_DIR, "report.md")
NOTES_TXT = os.path.join(INPUTS_DIR, "notes.txt")
IMAGE_JPG = os.path.join(INPUTS_DIR, "image.jpg")
PREVIOUS_STATE = os.path.join(PROJECT_DIR, "previous_state.json")


def test_python3_available():
    assert shutil.which("python3") is not None, "python3 binary not found in PATH."


def test_llama_cloud_managed_index_importable():
    """The LlamaCloudIndex SDK class must be importable from llama_index.indices.managed.llama_cloud."""
    module = importlib.import_module("llama_index.indices.managed.llama_cloud")
    assert hasattr(module, "LlamaCloudIndex"), (
        "llama_index.indices.managed.llama_cloud does not expose LlamaCloudIndex; "
        "the managed-index SDK package is not installed correctly."
    )


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_inputs_dir_exists():
    assert os.path.isdir(INPUTS_DIR), (
        f"Inputs directory {INPUTS_DIR} does not exist."
    )


def test_report_md_initial_content():
    assert os.path.isfile(REPORT_MD), f"Pre-existing file {REPORT_MD} is missing."
    with open(REPORT_MD, "rb") as f:
        content = f.read()
    assert content == b"# Report\nQ3 numbers are strong.", (
        f"Initial contents of {REPORT_MD} do not match the expected fixture bytes."
    )


def test_notes_txt_initial_content():
    assert os.path.isfile(NOTES_TXT), f"Pre-existing file {NOTES_TXT} is missing."
    with open(NOTES_TXT, "rb") as f:
        content = f.read()
    assert content == b"Internal notes.", (
        f"Initial contents of {NOTES_TXT} do not match the expected fixture bytes."
    )


def test_image_jpg_initial_content():
    assert os.path.isfile(IMAGE_JPG), f"Pre-existing file {IMAGE_JPG} is missing."
    with open(IMAGE_JPG, "rb") as f:
        content = f.read()
    assert content == b"fake jpg bytes", (
        f"Initial contents of {IMAGE_JPG} do not match the expected fixture bytes."
    )


def test_previous_state_json_initial_content():
    """The baseline previous_state.json must list report.md (with the current on-disk SHA-256)
    and a stale archive.txt entry whose previous_sha256 is the all-zeros placeholder."""
    assert os.path.isfile(PREVIOUS_STATE), (
        f"Pre-existing baseline file {PREVIOUS_STATE} is missing."
    )
    with open(PREVIOUS_STATE, "r", encoding="utf-8") as f:
        state = json.load(f)
    assert isinstance(state, dict), (
        f"{PREVIOUS_STATE} must be a JSON object at the top level."
    )
    assert "files" in state and isinstance(state["files"], list), (
        f"{PREVIOUS_STATE} must contain a 'files' list."
    )
    files_by_name = {entry["file_name"]: entry for entry in state["files"]}
    assert "report.md" in files_by_name, (
        f"{PREVIOUS_STATE} must contain a baseline entry for report.md."
    )
    assert "archive.txt" in files_by_name, (
        f"{PREVIOUS_STATE} must contain a stale baseline entry for archive.txt."
    )
    with open(REPORT_MD, "rb") as f:
        report_sha = hashlib.sha256(f.read()).hexdigest()
    assert files_by_name["report.md"]["sha256"] == report_sha, (
        "previous_state.json baseline sha256 for report.md must equal the current on-disk SHA-256 "
        "so that report.md is classified as UNCHANGED."
    )
    assert files_by_name["archive.txt"]["sha256"] == (
        "0000000000000000000000000000000000000000000000000000000000000000"
    ), (
        "previous_state.json baseline sha256 for archive.txt must be the all-zeros placeholder "
        "documented in the task."
    )
