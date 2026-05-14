import json
import os
import subprocess
import pytest

PROJECT_DIR = "/home/user/region_setup"
CLIENT_FACTORY_PATH = os.path.join(PROJECT_DIR, "client_factory.py")
RUN_PATH = os.path.join(PROJECT_DIR, "run.py")
RESOLVED_NA_PATH = os.path.join(PROJECT_DIR, "resolved_na.json")
RESOLVED_EU_PATH = os.path.join(PROJECT_DIR, "resolved_eu.json")

NA_BASE_URL = "https://api.cloud.llamaindex.ai"
EU_BASE_URL = "https://api.cloud.eu.llamaindex.ai"


@pytest.fixture(scope="module", autouse=True)
def run_runner_for_both_regions():
    """Ensure the user's runner has produced resolved_na.json and resolved_eu.json.

    The runner may already have been executed by the agent; if the output files are missing
    we invoke it ourselves so the verification can inspect them.
    """
    for region, out_path in [("na", RESOLVED_NA_PATH), ("eu", RESOLVED_EU_PATH)]:
        if not os.path.isfile(out_path) and os.path.isfile(RUN_PATH):
            subprocess.run(
                ["python3", "run.py", region],
                cwd=PROJECT_DIR,
                capture_output=True,
                text=True,
                timeout=60,
            )
    yield


def test_client_factory_module_exists():
    assert os.path.isfile(CLIENT_FACTORY_PATH), (
        f"Expected module {CLIENT_FACTORY_PATH}, but it was not found."
    )


def test_run_script_exists():
    assert os.path.isfile(RUN_PATH), (
        f"Expected runner script {RUN_PATH}, but it was not found."
    )


def test_client_factory_uses_llama_cloud_sdk():
    with open(CLIENT_FACTORY_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    assert "from llama_cloud import LlamaCloud" in content, (
        f"{CLIENT_FACTORY_PATH} must contain 'from llama_cloud import LlamaCloud'."
    )


def test_client_factory_does_not_hardcode_api_key():
    with open(CLIENT_FACTORY_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    assert "llx-" not in content, (
        f"{CLIENT_FACTORY_PATH} appears to hardcode a LlamaCloud API key (found 'llx-' prefix). "
        "It must rely on the LLAMA_CLOUD_API_KEY environment variable."
    )


def test_run_script_imports_client_factory():
    with open(RUN_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    assert "from client_factory" in content, (
        f"{RUN_PATH} must import from client_factory (string 'from client_factory')."
    )


def test_client_factory_module_constants_via_subprocess():
    """Priority 1 — exercise the user's module directly via Python and validate constants."""
    code = (
        "import sys; sys.path.insert(0, '/home/user/region_setup'); "
        "import client_factory; "
        "print('NA=' + client_factory.NA_BASE_URL); "
        "print('EU=' + client_factory.EU_BASE_URL)"
    )
    result = subprocess.run(
        ["python3", "-c", code],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
    )
    assert result.returncode == 0, (
        f"Importing client_factory failed. stderr: {result.stderr}"
    )
    assert f"NA={NA_BASE_URL}" in result.stdout, (
        f"Expected NA_BASE_URL == {NA_BASE_URL!r}. stdout: {result.stdout!r}"
    )
    assert f"EU={EU_BASE_URL}" in result.stdout, (
        f"Expected EU_BASE_URL == {EU_BASE_URL!r}. stdout: {result.stdout!r}"
    )


def test_resolve_base_url_eu_lowercase():
    code = (
        "import sys; sys.path.insert(0, '/home/user/region_setup'); "
        "import client_factory; "
        "print(client_factory.resolve_base_url('eu'))"
    )
    result = subprocess.run(
        ["python3", "-c", code],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
    )
    assert result.returncode == 0, (
        f"resolve_base_url('eu') call failed. stderr: {result.stderr}"
    )
    assert result.stdout.strip() == EU_BASE_URL, (
        f"resolve_base_url('eu') must return {EU_BASE_URL!r}. Got: {result.stdout!r}"
    )


def test_resolve_base_url_eu_case_insensitive():
    code = (
        "import sys; sys.path.insert(0, '/home/user/region_setup'); "
        "import client_factory; "
        "print(client_factory.resolve_base_url('EU'))"
    )
    result = subprocess.run(
        ["python3", "-c", code],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
    )
    assert result.returncode == 0, (
        f"resolve_base_url('EU') call failed. stderr: {result.stderr}"
    )
    assert result.stdout.strip() == EU_BASE_URL, (
        f"resolve_base_url('EU') must be case-insensitive and return {EU_BASE_URL!r}. "
        f"Got: {result.stdout!r}"
    )


def test_resolve_base_url_na_default():
    code = (
        "import sys; sys.path.insert(0, '/home/user/region_setup'); "
        "import client_factory; "
        "print(client_factory.resolve_base_url('na'))"
    )
    result = subprocess.run(
        ["python3", "-c", code],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
    )
    assert result.returncode == 0, (
        f"resolve_base_url('na') call failed. stderr: {result.stderr}"
    )
    assert result.stdout.strip() == NA_BASE_URL, (
        f"resolve_base_url('na') must return {NA_BASE_URL!r}. Got: {result.stdout!r}"
    )


def test_resolve_base_url_non_eu_falls_back_to_na():
    code = (
        "import sys; sys.path.insert(0, '/home/user/region_setup'); "
        "import client_factory; "
        "print(client_factory.resolve_base_url('us'))"
    )
    result = subprocess.run(
        ["python3", "-c", code],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
    )
    assert result.returncode == 0, (
        f"resolve_base_url('us') call failed. stderr: {result.stderr}"
    )
    assert result.stdout.strip() == NA_BASE_URL, (
        "Any input other than the literal 'eu' (case-insensitive) must fall back to the NA URL. "
        f"resolve_base_url('us') returned: {result.stdout!r}"
    )


def test_make_client_returns_llama_cloud_instance():
    code = (
        "import sys; sys.path.insert(0, '/home/user/region_setup'); "
        "import client_factory; "
        "client = client_factory.make_client('eu'); "
        "print(type(client).__name__)"
    )
    result = subprocess.run(
        ["python3", "-c", code],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
    )
    assert result.returncode == 0, (
        f"make_client('eu') call failed. stderr: {result.stderr}"
    )
    assert result.stdout.strip() == "LlamaCloud", (
        f"make_client must return an instance of llama_cloud.LlamaCloud "
        f"(type name 'LlamaCloud'). Got: {result.stdout!r}"
    )


def test_resolved_na_json_exists_and_valid():
    assert os.path.isfile(RESOLVED_NA_PATH), (
        f"Expected output file {RESOLVED_NA_PATH} after running 'python3 run.py na'."
    )
    with open(RESOLVED_NA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, dict), (
        f"{RESOLVED_NA_PATH} must contain a JSON object. Got: {type(data).__name__}"
    )
    assert data.get("region") == "na", (
        f"{RESOLVED_NA_PATH}: expected region == 'na', got: {data.get('region')!r}"
    )
    assert data.get("base_url") == NA_BASE_URL, (
        f"{RESOLVED_NA_PATH}: expected base_url == {NA_BASE_URL!r}, "
        f"got: {data.get('base_url')!r}"
    )
    assert data.get("client_type") == "LlamaCloud", (
        f"{RESOLVED_NA_PATH}: expected client_type == 'LlamaCloud', "
        f"got: {data.get('client_type')!r}"
    )


def test_resolved_eu_json_exists_and_valid():
    assert os.path.isfile(RESOLVED_EU_PATH), (
        f"Expected output file {RESOLVED_EU_PATH} after running 'python3 run.py eu'."
    )
    with open(RESOLVED_EU_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, dict), (
        f"{RESOLVED_EU_PATH} must contain a JSON object. Got: {type(data).__name__}"
    )
    assert data.get("region") == "eu", (
        f"{RESOLVED_EU_PATH}: expected region == 'eu', got: {data.get('region')!r}"
    )
    assert data.get("base_url") == EU_BASE_URL, (
        f"{RESOLVED_EU_PATH}: expected base_url == {EU_BASE_URL!r}, "
        f"got: {data.get('base_url')!r}"
    )
    assert data.get("client_type") == "LlamaCloud", (
        f"{RESOLVED_EU_PATH}: expected client_type == 'LlamaCloud', "
        f"got: {data.get('client_type')!r}"
    )
