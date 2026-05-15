import json
import os
import subprocess

import pytest

PROJECT_DIR = "/home/user/myproject"
SCRIPT_PATH = os.path.join(PROJECT_DIR, "region_client.py")
US_OUTPUT = os.path.join(PROJECT_DIR, "us.json")
EU_OUTPUT = os.path.join(PROJECT_DIR, "eu.json")
BAD_OUTPUT = os.path.join(PROJECT_DIR, "bad.json")

US_BASE_URL = "https://api.cloud.llamaindex.ai"
EU_BASE_URL = "https://api.cloud.eu.llamaindex.ai"


def _cleanup_output(path):
    if os.path.isfile(path):
        os.remove(path)


@pytest.fixture(scope="module")
def run_us_with_check():
    """Run with --region us --check and return the subprocess result."""
    _cleanup_output(US_OUTPUT)
    assert os.path.isfile(SCRIPT_PATH), (
        f"Expected user-provided script at {SCRIPT_PATH}; it was not found."
    )
    result = subprocess.run(
        [
            "python3",
            "region_client.py",
            "--region",
            "us",
            "--check",
            "--output",
            US_OUTPUT,
        ],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
        timeout=300,
    )
    return result


@pytest.fixture(scope="module")
def run_eu_no_check():
    """Run with --region eu (no --check) and return the subprocess result."""
    _cleanup_output(EU_OUTPUT)
    assert os.path.isfile(SCRIPT_PATH), (
        f"Expected user-provided script at {SCRIPT_PATH}; it was not found."
    )
    result = subprocess.run(
        [
            "python3",
            "region_client.py",
            "--region",
            "eu",
            "--output",
            EU_OUTPUT,
        ],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
        timeout=120,
    )
    return result


@pytest.fixture(scope="module")
def run_us_mixed_case_no_check():
    """Run with --region US (mixed case, no --check)."""
    _cleanup_output(US_OUTPUT)
    assert os.path.isfile(SCRIPT_PATH), (
        f"Expected user-provided script at {SCRIPT_PATH}; it was not found."
    )
    result = subprocess.run(
        [
            "python3",
            "region_client.py",
            "--region",
            "US",
            "--output",
            US_OUTPUT,
        ],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
        timeout=120,
    )
    return result


# ----- Step 1: NA with --check -----


def test_us_check_exit_zero(run_us_with_check):
    assert run_us_with_check.returncode == 0, (
        "Expected `region_client.py --region us --check` to exit 0, "
        f"got {run_us_with_check.returncode}. "
        f"stdout={run_us_with_check.stdout!r} stderr={run_us_with_check.stderr!r}"
    )


def test_us_check_stdout_line(run_us_with_check):
    expected_line = f"Region: us | Base URL: {US_BASE_URL}"
    stdout_lines = [line.strip() for line in run_us_with_check.stdout.splitlines()]
    assert expected_line in stdout_lines, (
        f"Expected stdout to contain the exact line {expected_line!r}; "
        f"got stdout lines: {stdout_lines!r}"
    )


def test_us_check_output_json(run_us_with_check):
    assert os.path.isfile(US_OUTPUT), (
        f"Expected output file {US_OUTPUT} to be created by region_client.py."
    )
    with open(US_OUTPUT, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data.get("region") == "us", (
        f"Expected JSON field 'region' to be 'us'; got {data.get('region')!r}"
    )
    assert data.get("base_url") == US_BASE_URL, (
        f"Expected JSON field 'base_url' to be {US_BASE_URL!r}; "
        f"got {data.get('base_url')!r}"
    )
    assert data.get("connection_verified") is True, (
        "Expected JSON field 'connection_verified' to be boolean true after "
        f"--check; got {data.get('connection_verified')!r} "
        f"(type {type(data.get('connection_verified')).__name__})."
    )
    project_count = data.get("project_count")
    assert isinstance(project_count, int) and not isinstance(project_count, bool), (
        f"Expected JSON field 'project_count' to be an integer; "
        f"got {project_count!r} (type {type(project_count).__name__})."
    )
    assert project_count >= 1, (
        f"Expected JSON field 'project_count' to be >= 1 for the configured "
        f"LLAMA_CLOUD_API_KEY; got {project_count}."
    )


# ----- Step 2: EU without --check -----


def test_eu_no_check_exit_zero(run_eu_no_check):
    assert run_eu_no_check.returncode == 0, (
        "Expected `region_client.py --region eu` to exit 0, "
        f"got {run_eu_no_check.returncode}. "
        f"stdout={run_eu_no_check.stdout!r} stderr={run_eu_no_check.stderr!r}"
    )


def test_eu_no_check_stdout_line(run_eu_no_check):
    expected_line = f"Region: eu | Base URL: {EU_BASE_URL}"
    stdout_lines = [line.strip() for line in run_eu_no_check.stdout.splitlines()]
    assert expected_line in stdout_lines, (
        f"Expected stdout to contain the exact line {expected_line!r}; "
        f"got stdout lines: {stdout_lines!r}"
    )


def test_eu_no_check_output_json(run_eu_no_check):
    assert os.path.isfile(EU_OUTPUT), (
        f"Expected output file {EU_OUTPUT} to be created by region_client.py."
    )
    with open(EU_OUTPUT, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data.get("region") == "eu", (
        f"Expected JSON field 'region' to be 'eu'; got {data.get('region')!r}"
    )
    assert data.get("base_url") == EU_BASE_URL, (
        f"Expected JSON field 'base_url' to be {EU_BASE_URL!r}; "
        f"got {data.get('base_url')!r}"
    )
    assert data.get("connection_verified") is False, (
        "Expected JSON field 'connection_verified' to be boolean false when "
        f"--check is not supplied; got {data.get('connection_verified')!r} "
        f"(type {type(data.get('connection_verified')).__name__})."
    )
    project_count = data.get("project_count")
    assert isinstance(project_count, int) and not isinstance(project_count, bool), (
        f"Expected JSON field 'project_count' to be an integer; "
        f"got {project_count!r} (type {type(project_count).__name__})."
    )
    assert project_count == 0, (
        f"Expected JSON field 'project_count' to be 0 when --check is not "
        f"supplied; got {project_count}."
    )


# ----- Step 3: mixed-case US without --check -----


def test_us_mixed_case_exit_zero(run_us_mixed_case_no_check):
    assert run_us_mixed_case_no_check.returncode == 0, (
        "Expected `region_client.py --region US` (mixed case) to exit 0, "
        f"got {run_us_mixed_case_no_check.returncode}. "
        f"stdout={run_us_mixed_case_no_check.stdout!r} "
        f"stderr={run_us_mixed_case_no_check.stderr!r}"
    )


def test_us_mixed_case_stdout_line(run_us_mixed_case_no_check):
    expected_line = f"Region: us | Base URL: {US_BASE_URL}"
    stdout_lines = [
        line.strip() for line in run_us_mixed_case_no_check.stdout.splitlines()
    ]
    assert expected_line in stdout_lines, (
        "Expected stdout from mixed-case run to contain the exact line "
        f"{expected_line!r} (lowercased); got stdout lines: {stdout_lines!r}"
    )


def test_us_mixed_case_output_json(run_us_mixed_case_no_check):
    assert os.path.isfile(US_OUTPUT), (
        f"Expected output file {US_OUTPUT} to be created by region_client.py."
    )
    with open(US_OUTPUT, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data.get("region") == "us", (
        "Expected JSON field 'region' to be lowercased 'us' even when the "
        f"input was 'US'; got {data.get('region')!r}"
    )
    assert data.get("base_url") == US_BASE_URL, (
        f"Expected JSON field 'base_url' to be {US_BASE_URL!r}; "
        f"got {data.get('base_url')!r}"
    )
    assert data.get("connection_verified") is False, (
        "Expected JSON field 'connection_verified' to be boolean false when "
        f"--check is not supplied; got {data.get('connection_verified')!r}"
    )
    assert data.get("project_count") == 0, (
        "Expected JSON field 'project_count' to be 0 when --check is not "
        f"supplied; got {data.get('project_count')!r}"
    )


# ----- Step 4: unknown region must fail -----


def test_unknown_region_exits_nonzero():
    _cleanup_output(BAD_OUTPUT)
    result = subprocess.run(
        [
            "python3",
            "region_client.py",
            "--region",
            "apac",
            "--output",
            BAD_OUTPUT,
        ],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
        timeout=60,
    )
    assert result.returncode != 0, (
        "Expected region_client.py to exit with a non-zero status code when "
        f"given an unknown region; got returncode={result.returncode}, "
        f"stdout={result.stdout!r}, stderr={result.stderr!r}"
    )


# ----- Step 5: source-code inspection -----


def test_script_source_uses_llama_cloud_sdk():
    with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
        source = f.read()
    assert "from llama_cloud import LlamaCloud" in source, (
        "region_client.py must import LlamaCloud from llama_cloud "
        "(expected the line `from llama_cloud import LlamaCloud`)."
    )
    assert US_BASE_URL in source, (
        f"region_client.py must reference the NA base URL literal {US_BASE_URL!r} "
        "directly in its source."
    )
    assert EU_BASE_URL in source, (
        f"region_client.py must reference the EU base URL literal {EU_BASE_URL!r} "
        "directly in its source."
    )
    assert "base_url=" in source, (
        "region_client.py must construct the LlamaCloud client with a "
        "`base_url=` keyword argument."
    )
