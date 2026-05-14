import importlib
import os
import shutil

import pytest

PROJECT_DIR = "/home/user/parse_planner"
INPUTS_DIR = os.path.join(PROJECT_DIR, "inputs")
DATA_TXT = os.path.join(INPUTS_DIR, "data.txt")
NOTES_MD = os.path.join(INPUTS_DIR, "notes.md")
IMAGE_JPG = os.path.join(INPUTS_DIR, "image.jpg")


def test_python3_available():
    assert shutil.which("python3") is not None, "python3 binary not found in PATH."


def test_llama_cloud_services_importable():
    """The LlamaParse SDK class must be importable from llama_cloud_services."""
    module = importlib.import_module("llama_cloud_services")
    assert hasattr(module, "LlamaParse"), (
        "llama_cloud_services package does not expose LlamaParse; "
        "the LlamaCloud SDK is not installed correctly."
    )


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_inputs_dir_exists():
    assert os.path.isdir(INPUTS_DIR), (
        f"Inputs directory {INPUTS_DIR} does not exist."
    )


def test_data_txt_initial_content():
    assert os.path.isfile(DATA_TXT), f"Pre-existing file {DATA_TXT} is missing."
    with open(DATA_TXT, "rb") as f:
        content = f.read()
    assert content == b"Sample data for parsing.", (
        f"Initial contents of {DATA_TXT} do not match the expected fixture bytes."
    )


def test_notes_md_initial_content():
    assert os.path.isfile(NOTES_MD), f"Pre-existing file {NOTES_MD} is missing."
    with open(NOTES_MD, "rb") as f:
        content = f.read()
    assert content == b"# Notes\nHello world", (
        f"Initial contents of {NOTES_MD} do not match the expected fixture bytes."
    )


def test_image_jpg_initial_content():
    assert os.path.isfile(IMAGE_JPG), f"Pre-existing file {IMAGE_JPG} is missing."
    with open(IMAGE_JPG, "rb") as f:
        content = f.read()
    assert content == b"fake image bytes", (
        f"Initial contents of {IMAGE_JPG} do not match the expected fixture bytes."
    )
