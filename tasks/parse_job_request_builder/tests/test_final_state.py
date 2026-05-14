import json
import os
import subprocess
import textwrap

import pytest

PROJECT_DIR = "/home/user/parse_requests"
CONFIGS_DIR = os.path.join(PROJECT_DIR, "configs")
SCRIPT_PATH = os.path.join(PROJECT_DIR, "build_requests.py")

VALID_CONFIG = os.path.join(CONFIGS_DIR, "valid.yaml")
BAD_TIER_CONFIG = os.path.join(CONFIGS_DIR, "bad_tier.yaml")
FAST_MARKDOWN_CONFIG = os.path.join(CONFIGS_DIR, "fast_markdown.yaml")
BAD_VERSION_CONFIG = os.path.join(CONFIGS_DIR, "bad_version.yaml")
MISSING_CONFIG = os.path.join(CONFIGS_DIR, "no_such_file.yaml")

VALID_OUTPUT = os.path.join(PROJECT_DIR, "plan.json")
BAD_TIER_OUTPUT = os.path.join(PROJECT_DIR, "bad_tier_plan.json")
FAST_MARKDOWN_OUTPUT = os.path.join(PROJECT_DIR, "fast_markdown_plan.json")
BAD_VERSION_OUTPUT = os.path.join(PROJECT_DIR, "bad_version_plan.json")
SHOULD_NOT_EXIST_OUTPUT = os.path.join(PROJECT_DIR, "should_not_exist.json")

# Each error-path config has prescribed contents in the task description. The
# verifier writes them to disk so the test does not depend on the agent having
# created the helper files in addition to the script.
ERROR_CONFIGS = {
    BAD_TIER_CONFIG: textwrap.dedent(
        """\
        requests:
          - file_id: file_xxx
            tier: premium
            version: latest
            expand: [markdown]
        """
    ),
    FAST_MARKDOWN_CONFIG: textwrap.dedent(
        """\
        requests:
          - file_id: file_yyy
            tier: fast
            version: latest
            expand: [text, markdown]
        """
    ),
    BAD_VERSION_CONFIG: textwrap.dedent(
        """\
        requests:
          - file_id: file_zzz
            tier: agentic
            version: jan-8-2026
            expand: [markdown]
        """
    ),
}


@pytest.fixture(autouse=True)
def setup_environment():
    """Remove stale outputs and (re)write the error-path YAML helpers so each
    test starts from a known state."""
    for path in (
        VALID_OUTPUT,
        BAD_TIER_OUTPUT,
        FAST_MARKDOWN_OUTPUT,
        BAD_VERSION_OUTPUT,
        SHOULD_NOT_EXIST_OUTPUT,
    ):
        if os.path.exists(path):
            os.remove(path)
    if os.path.exists(MISSING_CONFIG):
        os.remove(MISSING_CONFIG)
    os.makedirs(CONFIGS_DIR, exist_ok=True)
    for path, content in ERROR_CONFIGS.items():
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)
    yield


def test_script_exists():
    assert os.path.isfile(SCRIPT_PATH), (
        f"Expected the CLI script to exist at {SCRIPT_PATH}."
    )


def test_script_imports_llama_cloud_sdk():
    with open(SCRIPT_PATH, "r", encoding="utf-8") as fh:
        contents = fh.read()
    assert "from llama_cloud import LlamaCloud" in contents, (
        "Script must contain the verbatim import `from llama_cloud import "
        f"LlamaCloud` per the task description. Current contents:\n{contents}"
    )


def test_happy_path_run():
    result = subprocess.run(
        [
            "python3",
            SCRIPT_PATH,
            "--config",
            VALID_CONFIG,
            "--output",
            VALID_OUTPUT,
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Happy-path run should exit 0 but exited {result.returncode}. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    expected_stdout_line = (
        "Built 4 Parse v2 requests at "
        "/home/user/parse_requests/plan.json: "
        "fast=1 cost_effective=1 agentic=1 agentic_plus=1"
    )
    assert expected_stdout_line in result.stdout, (
        f"Expected stdout to contain {expected_stdout_line!r}; got stdout={result.stdout!r}"
    )
    assert os.path.isfile(VALID_OUTPUT), (
        f"Expected the output plan file {VALID_OUTPUT} to be created."
    )
    with open(VALID_OUTPUT, "r", encoding="utf-8") as fh:
        payload = json.load(fh)
    assert set(payload.keys()) == {"requests", "summary"}, (
        f"Expected top-level keys to be exactly 'requests' and 'summary'; got {sorted(payload.keys())!r}"
    )
    expected_requests = [
        {
            "file_id": "file_aaa",
            "tier": "agentic",
            "version": "latest",
            "expand": ["text", "markdown"],
        },
        {
            "file_id": "file_bbb",
            "tier": "agentic_plus",
            "version": "2026-01-08",
            "expand": ["markdown", "items"],
        },
        {
            "file_id": "file_ccc",
            "tier": "fast",
            "version": "latest",
            "expand": ["text"],
        },
        {
            "file_id": "file_ddd",
            "tier": "cost_effective",
            "version": "latest",
            "expand": [],
        },
    ]
    assert payload["requests"] == expected_requests, (
        f"Expected `requests` to equal {expected_requests!r}; got {payload['requests']!r}"
    )
    expected_summary = {
        "total": 4,
        "by_tier": {
            "fast": 1,
            "cost_effective": 1,
            "agentic": 1,
            "agentic_plus": 1,
        },
    }
    assert payload["summary"] == expected_summary, (
        f"Expected `summary` to equal {expected_summary!r}; got {payload['summary']!r}"
    )


def test_bad_tier_validation():
    result = subprocess.run(
        [
            "python3",
            SCRIPT_PATH,
            "--config",
            BAD_TIER_CONFIG,
            "--output",
            BAD_TIER_OUTPUT,
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0, (
        f"Bad-tier run should exit non-zero but exited {result.returncode}. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    expected_err = (
        "Error: requests[0].tier must be one of: "
        "agentic, agentic_plus, cost_effective, fast"
    )
    assert expected_err in result.stderr, (
        f"Expected stderr to contain {expected_err!r}; got stderr={result.stderr!r}"
    )
    assert not os.path.exists(BAD_TIER_OUTPUT), (
        f"The output file {BAD_TIER_OUTPUT} must NOT be created when validation fails."
    )


def test_fast_tier_markdown_validation():
    result = subprocess.run(
        [
            "python3",
            SCRIPT_PATH,
            "--config",
            FAST_MARKDOWN_CONFIG,
            "--output",
            FAST_MARKDOWN_OUTPUT,
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0, (
        f"Fast/markdown run should exit non-zero but exited {result.returncode}. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    expected_err = (
        "Error: requests[0] uses tier 'fast' which does not support "
        "'markdown' in expand"
    )
    assert expected_err in result.stderr, (
        f"Expected stderr to contain {expected_err!r}; got stderr={result.stderr!r}"
    )
    assert not os.path.exists(FAST_MARKDOWN_OUTPUT), (
        f"The output file {FAST_MARKDOWN_OUTPUT} must NOT be created when validation fails."
    )


def test_bad_version_validation():
    result = subprocess.run(
        [
            "python3",
            SCRIPT_PATH,
            "--config",
            BAD_VERSION_CONFIG,
            "--output",
            BAD_VERSION_OUTPUT,
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0, (
        f"Bad-version run should exit non-zero but exited {result.returncode}. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    expected_err = (
        "Error: requests[0].version must be 'latest' or a date string "
        "in YYYY-MM-DD format"
    )
    assert expected_err in result.stderr, (
        f"Expected stderr to contain {expected_err!r}; got stderr={result.stderr!r}"
    )
    assert not os.path.exists(BAD_VERSION_OUTPUT), (
        f"The output file {BAD_VERSION_OUTPUT} must NOT be created when validation fails."
    )


def test_missing_config_validation():
    assert not os.path.exists(MISSING_CONFIG), (
        f"Pre-test invariant: {MISSING_CONFIG} must not exist."
    )
    result = subprocess.run(
        [
            "python3",
            SCRIPT_PATH,
            "--config",
            MISSING_CONFIG,
            "--output",
            SHOULD_NOT_EXIST_OUTPUT,
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0, (
        f"Missing-config run should exit non-zero but exited {result.returncode}. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    expected_err = (
        f"Error: config file not found: {MISSING_CONFIG}"
    )
    assert expected_err in result.stderr, (
        f"Expected stderr to contain {expected_err!r}; got stderr={result.stderr!r}"
    )
    assert not os.path.exists(SHOULD_NOT_EXIST_OUTPUT), (
        f"The output file {SHOULD_NOT_EXIST_OUTPUT} must NOT be created when the config is missing."
    )
