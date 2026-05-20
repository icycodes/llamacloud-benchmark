import json
import os
import re
import subprocess

import pytest


PROJECT_DIR = "/home/user/myproject"
SCRIPT_PATH = os.path.join(PROJECT_DIR, "regional_client.py")

US_BASE_URL = "https://api.cloud.llamaindex.ai"
EU_BASE_URL = "https://api.cloud.eu.llamaindex.ai"


def _run_cli(*extra_args, env=None):
    cmd = ["python3", SCRIPT_PATH, *extra_args]
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
        env=env,
    )


def _parse_stdout_json(stdout):
    stdout = stdout.strip()
    assert stdout, "CLI produced no stdout output."
    # The CLI MUST print exactly one JSON object. Take the last non-empty line.
    last_line = [line for line in stdout.splitlines() if line.strip()][-1]
    try:
        return json.loads(last_line)
    except json.JSONDecodeError as exc:  # pragma: no cover - message in failure
        raise AssertionError(
            f"Expected the CLI to print a single JSON object on stdout; "
            f"got: {stdout!r} (parse error: {exc})"
        )


def test_script_file_exists():
    assert os.path.isfile(SCRIPT_PATH), (
        f"Expected CLI script at {SCRIPT_PATH}, but it does not exist."
    )


def test_us_region_output():
    result = _run_cli("--region", "us")
    assert result.returncode == 0, (
        f"`regional_client.py --region us` exited with {result.returncode}. "
        f"stderr: {result.stderr!r}"
    )
    payload = _parse_stdout_json(result.stdout)
    assert payload.get("region") == "us", (
        f"Expected `region` field to be 'us', got: {payload!r}"
    )
    assert payload.get("base_url") == US_BASE_URL, (
        f"Expected `base_url` field to be {US_BASE_URL!r}, got: {payload!r}"
    )
    assert payload.get("parser_base_url") == US_BASE_URL, (
        "Expected `parser_base_url` (read back from the LlamaParse instance) "
        f"to be {US_BASE_URL!r}, got: {payload!r}"
    )


def test_eu_region_output():
    result = _run_cli("--region", "eu")
    assert result.returncode == 0, (
        f"`regional_client.py --region eu` exited with {result.returncode}. "
        f"stderr: {result.stderr!r}"
    )
    payload = _parse_stdout_json(result.stdout)
    assert payload.get("region") == "eu", (
        f"Expected `region` field to be 'eu', got: {payload!r}"
    )
    assert payload.get("base_url") == EU_BASE_URL, (
        f"Expected `base_url` field to be {EU_BASE_URL!r}, got: {payload!r}"
    )
    assert payload.get("parser_base_url") == EU_BASE_URL, (
        "Expected `parser_base_url` (read back from the LlamaParse instance) "
        f"to be {EU_BASE_URL!r}, got: {payload!r}"
    )


def test_region_argument_case_insensitive():
    result = _run_cli("--region", "EU")
    assert result.returncode == 0, (
        f"`regional_client.py --region EU` exited with {result.returncode}. "
        f"stderr: {result.stderr!r}"
    )
    payload = _parse_stdout_json(result.stdout)
    assert payload.get("region") == "eu", (
        "Expected the CLI to normalize the region value to lowercase 'eu' "
        f"when passed --region EU, got: {payload!r}"
    )
    assert payload.get("base_url") == EU_BASE_URL, (
        f"Expected base_url to be {EU_BASE_URL!r} for --region EU, "
        f"got: {payload!r}"
    )
    assert payload.get("parser_base_url") == EU_BASE_URL, (
        "Expected parser_base_url to be the EU URL for --region EU, "
        f"got: {payload!r}"
    )


def test_unsupported_region_exits_non_zero():
    result = _run_cli("--region", "apac")
    assert result.returncode != 0, (
        "Expected `regional_client.py --region apac` to exit with a non-zero "
        f"status code, got 0. stdout: {result.stdout!r}"
    )
    combined = (result.stderr or "")
    assert re.search(r"unsupported region", combined, re.IGNORECASE), (
        "Expected an error message containing the substring "
        f"'unsupported region' on stderr, got: {combined!r}"
    )


def test_eu_url_matches_sdk_constant():
    """Ensure the EU URL the CLI uses matches the SDK's EU_BASE_URL constant."""
    probe = subprocess.run(
        [
            "python3",
            "-c",
            "from llama_cloud_services import EU_BASE_URL; print(EU_BASE_URL)",
        ],
        capture_output=True,
        text=True,
    )
    assert probe.returncode == 0, (
        "Failed to import EU_BASE_URL from llama_cloud_services: "
        f"{probe.stderr!r}"
    )
    sdk_eu = probe.stdout.strip()
    assert sdk_eu == EU_BASE_URL, (
        f"SDK EU_BASE_URL value drifted; expected {EU_BASE_URL!r}, got "
        f"{sdk_eu!r}."
    )

    result = _run_cli("--region", "eu")
    payload = _parse_stdout_json(result.stdout)
    assert payload.get("base_url") == sdk_eu, (
        "Expected the CLI's `base_url` for EU to match the SDK's EU_BASE_URL "
        f"constant ({sdk_eu!r}); got {payload!r}."
    )
