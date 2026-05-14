import json
import os
import subprocess
import sys
import textwrap

import pytest

PROJECT_DIR = "/home/user/mcp_config_builder"
CONFIGS_DIR = os.path.join(PROJECT_DIR, "configs")
SCRIPT = os.path.join(PROJECT_DIR, "build_mcp_config.py")

VALID_CONFIG = os.path.join(CONFIGS_DIR, "valid.yaml")
DUP_CONFIG = os.path.join(CONFIGS_DIR, "duplicate_name.yaml")
BAD_TOPK_CONFIG = os.path.join(CONFIGS_DIR, "bad_topk.yaml")
EMPTY_DESC_CONFIG = os.path.join(CONFIGS_DIR, "empty_description.yaml")
NO_SUCH_CONFIG = os.path.join(CONFIGS_DIR, "no_such_file.yaml")

MCP_JSON = os.path.join(PROJECT_DIR, "mcp.json")
DUP_PLAN = os.path.join(PROJECT_DIR, "dup_plan.json")
BAD_TOPK_PLAN = os.path.join(PROJECT_DIR, "bad_topk_plan.json")
EMPTY_DESC_PLAN = os.path.join(PROJECT_DIR, "empty_desc_plan.json")
SHOULD_NOT_EXIST = os.path.join(PROJECT_DIR, "should_not_exist.json")


def _remove(path: str) -> None:
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture(autouse=True)
def cleanup():
    """Remove any output artifacts before each test to ensure deterministic runs."""
    for path in (MCP_JSON, DUP_PLAN, BAD_TOPK_PLAN, EMPTY_DESC_PLAN, SHOULD_NOT_EXIST):
        _remove(path)
    yield


def _run(args):
    return subprocess.run(
        [sys.executable, SCRIPT, *args],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
    )


def test_script_exists():
    assert os.path.isfile(SCRIPT), f"Build script {SCRIPT} does not exist."


def test_sdk_import_string_present():
    """The script source must demonstrate the LlamaCloud SDK import."""
    with open(SCRIPT, "r", encoding="utf-8") as f:
        source = f.read()
    assert "from llama_cloud.client import LlamaCloud" in source, (
        "Expected the script to contain the verbatim substring "
        "'from llama_cloud.client import LlamaCloud' to demonstrate SDK availability."
    )


def test_happy_path_run():
    """Running on the starter valid.yaml must succeed with the exact expected stdout."""
    result = _run(["--config", VALID_CONFIG, "--output", MCP_JSON])
    assert result.returncode == 0, (
        f"Expected exit code 0 on the happy path, got {result.returncode}. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    expected_stdout = (
        f"MCP config written to {MCP_JSON}: server=llamacloud indices=2\n"
    )
    assert result.stdout == expected_stdout, (
        f"Unexpected stdout. Expected exactly {expected_stdout!r}, got {result.stdout!r}."
    )
    assert os.path.isfile(MCP_JSON), f"Expected {MCP_JSON} to be created."


def test_happy_path_output_structure():
    """The generated mcp.json must match the exact expected structure."""
    result = _run(["--config", VALID_CONFIG, "--output", MCP_JSON])
    assert result.returncode == 0, (
        f"Happy-path run must succeed. stdout={result.stdout!r} stderr={result.stderr!r}"
    )

    with open(MCP_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert set(data.keys()) == {"mcpServers"}, (
        f"Expected top-level keys to be exactly {{'mcpServers'}}, got {set(data.keys())}."
    )
    servers = data["mcpServers"]
    assert isinstance(servers, dict) and set(servers.keys()) == {"llamacloud"}, (
        f"Expected mcpServers to have exactly one key 'llamacloud', got {list(servers.keys())}."
    )

    entry = servers["llamacloud"]
    assert entry.get("command") == "npx", (
        f"Expected mcpServers.llamacloud.command == 'npx', got {entry.get('command')!r}."
    )

    expected_args = [
        "-y",
        "@llamaindex/mcp-server-llamacloud",
        "--index",
        "10k-SEC-Tesla",
        "--description",
        "10k SEC documents from 2023 for Tesla",
        "--topK",
        "5",
        "--index",
        "10k-SEC-Apple",
        "--description",
        "10k SEC documents from 2023 for Apple",
    ]
    assert entry.get("args") == expected_args, (
        "mcpServers.llamacloud.args mismatch.\n"
        f"Expected: {expected_args}\n"
        f"Actual:   {entry.get('args')}"
    )

    expected_env = {
        "LLAMA_CLOUD_PROJECT_NAME": "Financials",
        "LLAMA_CLOUD_API_KEY": "${LLAMA_CLOUD_API_KEY}",
    }
    assert entry.get("env") == expected_env, (
        "mcpServers.llamacloud.env mismatch.\n"
        f"Expected: {expected_env}\n"
        f"Actual:   {entry.get('env')}"
    )


def _write_fixture(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def test_validation_error_duplicate_name():
    _write_fixture(
        DUP_CONFIG,
        textwrap.dedent(
            """\
            server_name: llamacloud
            project_name: Financials
            indices:
              - name: 10k-SEC-Tesla
                description: 10k SEC documents from 2023 for Tesla
              - name: 10k-SEC-Tesla
                description: Duplicate entry
            """
        ),
    )

    result = _run(["--config", DUP_CONFIG, "--output", DUP_PLAN])
    assert result.returncode != 0, (
        f"Expected non-zero exit on duplicate index name, got {result.returncode}. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "Error: indices contains duplicate name: 10k-SEC-Tesla" in result.stderr, (
        f"Expected stderr to contain the duplicate-name error line, got {result.stderr!r}."
    )
    assert not os.path.exists(DUP_PLAN), (
        f"{DUP_PLAN} must NOT be created when validation fails."
    )


def test_validation_error_bad_topk():
    _write_fixture(
        BAD_TOPK_CONFIG,
        textwrap.dedent(
            """\
            server_name: llamacloud
            project_name: Financials
            indices:
              - name: 10k-SEC-Tesla
                description: 10k SEC documents from 2023 for Tesla
                top_k: 0
            """
        ),
    )

    result = _run(["--config", BAD_TOPK_CONFIG, "--output", BAD_TOPK_PLAN])
    assert result.returncode != 0, (
        f"Expected non-zero exit on invalid top_k, got {result.returncode}. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "Error: indices[0].top_k must be a positive integer" in result.stderr, (
        f"Expected stderr to contain the top_k error line, got {result.stderr!r}."
    )
    assert not os.path.exists(BAD_TOPK_PLAN), (
        f"{BAD_TOPK_PLAN} must NOT be created when validation fails."
    )


def test_validation_error_empty_description():
    _write_fixture(
        EMPTY_DESC_CONFIG,
        textwrap.dedent(
            """\
            server_name: llamacloud
            project_name: Financials
            indices:
              - name: 10k-SEC-Tesla
                description: ""
            """
        ),
    )

    result = _run(["--config", EMPTY_DESC_CONFIG, "--output", EMPTY_DESC_PLAN])
    assert result.returncode != 0, (
        f"Expected non-zero exit on empty description, got {result.returncode}. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "Error: indices[0].description must be a non-empty string" in result.stderr, (
        f"Expected stderr to contain the empty-description error line, got {result.stderr!r}."
    )
    assert not os.path.exists(EMPTY_DESC_PLAN), (
        f"{EMPTY_DESC_PLAN} must NOT be created when validation fails."
    )


def test_validation_error_missing_config_file():
    # Make sure the fixture really does not exist.
    if os.path.exists(NO_SUCH_CONFIG):
        os.remove(NO_SUCH_CONFIG)

    result = _run(["--config", NO_SUCH_CONFIG, "--output", SHOULD_NOT_EXIST])
    assert result.returncode != 0, (
        f"Expected non-zero exit when --config does not exist, got {result.returncode}. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    expected_err_line = f"Error: config file not found: {NO_SUCH_CONFIG}"
    assert expected_err_line in result.stderr, (
        f"Expected stderr to contain {expected_err_line!r}, got {result.stderr!r}."
    )
    assert not os.path.exists(SHOULD_NOT_EXIST), (
        f"{SHOULD_NOT_EXIST} must NOT be created when validation fails."
    )
