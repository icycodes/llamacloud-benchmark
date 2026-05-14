import json
import os
import subprocess

import pytest

PROJECT_DIR = "/home/user/llamacloud_region"
SCRIPT_PATH = os.path.join(PROJECT_DIR, "region_setup.py")
NA_REPORT = os.path.join(PROJECT_DIR, "na_report.json")
EU_REPORT = os.path.join(PROJECT_DIR, "eu_report.json")
INVALID_OUTPUT = "/tmp/should_not_exist.json"


@pytest.fixture(autouse=True)
def cleanup_outputs():
    """Remove any stale report files before each test run."""
    for path in (NA_REPORT, EU_REPORT, INVALID_OUTPUT):
        if os.path.exists(path):
            os.remove(path)
    yield


def test_script_exists():
    assert os.path.isfile(SCRIPT_PATH), (
        f"Expected the CLI script to exist at {SCRIPT_PATH}."
    )


def test_script_uses_llama_cloud_sdk():
    with open(SCRIPT_PATH, "r", encoding="utf-8") as fh:
        contents = fh.read()
    assert "from llama_cloud.client import LlamaCloud" in contents, (
        "Script must import `LlamaCloud` from `llama_cloud.client` per the task "
        f"description. Current contents:\n{contents}"
    )


def test_na_region_run():
    result = subprocess.run(
        [
            "python3",
            SCRIPT_PATH,
            "--region",
            "na",
            "--output",
            NA_REPORT,
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"NA region run should exit 0 but exited {result.returncode}. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    expected_stdout_line = (
        "Configured LlamaCloud client for region=NA "
        "base_url=https://api.cloud.llamaindex.ai"
    )
    assert expected_stdout_line in result.stdout, (
        f"Expected stdout to contain {expected_stdout_line!r}; got stdout={result.stdout!r}"
    )
    assert os.path.isfile(NA_REPORT), (
        f"Expected the NA report file {NA_REPORT} to be created."
    )
    with open(NA_REPORT, "r", encoding="utf-8") as fh:
        payload = json.load(fh)
    assert payload.get("region") == "NA", (
        f"Expected JSON field `region`==\"NA\" in {NA_REPORT}; got {payload!r}"
    )
    assert payload.get("base_url") == "https://api.cloud.llamaindex.ai", (
        f"Expected JSON field `base_url`==\"https://api.cloud.llamaindex.ai\" in "
        f"{NA_REPORT}; got {payload!r}"
    )
    assert payload.get("client_initialized") is True, (
        f"Expected JSON field `client_initialized`==true in {NA_REPORT}; "
        f"got {payload!r}"
    )


def test_eu_region_run_uppercase_input():
    result = subprocess.run(
        [
            "python3",
            SCRIPT_PATH,
            "--region",
            "EU",
            "--output",
            EU_REPORT,
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"EU region run should exit 0 but exited {result.returncode}. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    expected_stdout_line = (
        "Configured LlamaCloud client for region=EU "
        "base_url=https://api.cloud.eu.llamaindex.ai"
    )
    assert expected_stdout_line in result.stdout, (
        f"Expected stdout to contain {expected_stdout_line!r}; got stdout={result.stdout!r}"
    )
    assert os.path.isfile(EU_REPORT), (
        f"Expected the EU report file {EU_REPORT} to be created."
    )
    with open(EU_REPORT, "r", encoding="utf-8") as fh:
        payload = json.load(fh)
    assert payload.get("region") == "EU", (
        f"Expected JSON field `region`==\"EU\" in {EU_REPORT}; got {payload!r}"
    )
    assert payload.get("base_url") == "https://api.cloud.eu.llamaindex.ai", (
        f"Expected JSON field `base_url`==\"https://api.cloud.eu.llamaindex.ai\" in "
        f"{EU_REPORT}; got {payload!r}"
    )
    assert payload.get("client_initialized") is True, (
        f"Expected JSON field `client_initialized`==true in {EU_REPORT}; "
        f"got {payload!r}"
    )


def test_invalid_region_run():
    result = subprocess.run(
        [
            "python3",
            SCRIPT_PATH,
            "--region",
            "apac",
            "--output",
            INVALID_OUTPUT,
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0, (
        f"Invalid region run should exit non-zero but exited {result.returncode}. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "Error: unsupported region 'apac'. Use 'na' or 'eu'." in result.stderr, (
        f"Expected stderr to contain the specific error message; got stderr={result.stderr!r}"
    )
    assert not os.path.exists(INVALID_OUTPUT), (
        f"The output file {INVALID_OUTPUT} should NOT have been created for an "
        "invalid region argument."
    )
