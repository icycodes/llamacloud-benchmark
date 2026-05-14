import os
import shutil
import subprocess

PROJECT_DIR = "/home/user/parse_requests"
CONFIGS_DIR = os.path.join(PROJECT_DIR, "configs")
VALID_CONFIG = os.path.join(CONFIGS_DIR, "valid.yaml")


def test_python3_available():
    assert shutil.which("python3") is not None, (
        "python3 binary not found in PATH; required to run the CLI script."
    )


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Expected project directory {PROJECT_DIR} to exist in the initial state."
    )


def test_configs_directory_exists():
    assert os.path.isdir(CONFIGS_DIR), (
        f"Expected configs directory {CONFIGS_DIR} to exist in the initial state."
    )


def test_starter_valid_yaml_exists():
    assert os.path.isfile(VALID_CONFIG), (
        f"Expected starter YAML manifest {VALID_CONFIG} to exist in the initial state."
    )


def test_starter_valid_yaml_contents():
    """The starter manifest must describe four requests, one per tier, in the
    exact order documented in the task description."""
    import yaml  # PyYAML is installed in the environment

    with open(VALID_CONFIG, "r", encoding="utf-8") as fh:
        doc = yaml.safe_load(fh)

    assert isinstance(doc, dict), (
        f"Expected the YAML root of {VALID_CONFIG} to be a mapping; got: {type(doc).__name__}"
    )
    assert "requests" in doc, (
        f"Expected the YAML root of {VALID_CONFIG} to contain a `requests` key."
    )
    requests = doc["requests"]
    assert isinstance(requests, list) and len(requests) == 4, (
        f"Expected `requests` in {VALID_CONFIG} to be a list of length 4; got: {requests!r}"
    )

    # The fourth entry intentionally omits `expand` to verify the CLI defaults
    # missing `expand` to an empty list. The first three entries provide explicit
    # `expand` lists covering all the documented combinations.
    expected = [
        {"file_id": "file_aaa", "tier": "agentic", "version": "latest", "expand": ["text", "markdown"]},
        {"file_id": "file_bbb", "tier": "agentic_plus", "version": "2026-01-08", "expand": ["markdown", "items"]},
        {"file_id": "file_ccc", "tier": "fast", "version": "latest", "expand": ["text"]},
        {"file_id": "file_ddd", "tier": "cost_effective", "version": "latest"},
    ]
    for i, exp in enumerate(expected):
        entry = requests[i]
        assert isinstance(entry, dict), (
            f"Expected requests[{i}] in {VALID_CONFIG} to be a mapping; got: {entry!r}"
        )
        for key in ("file_id", "tier", "version"):
            assert key in entry, (
                f"Expected requests[{i}] in {VALID_CONFIG} to contain key '{key}'; got entry: {entry!r}"
            )
        assert entry["file_id"] == exp["file_id"], (
            f"Expected requests[{i}].file_id == {exp['file_id']!r} in {VALID_CONFIG}; got {entry['file_id']!r}"
        )
        assert entry["tier"] == exp["tier"], (
            f"Expected requests[{i}].tier == {exp['tier']!r} in {VALID_CONFIG}; got {entry['tier']!r}"
        )
        assert str(entry["version"]) == exp["version"], (
            f"Expected requests[{i}].version == {exp['version']!r} in {VALID_CONFIG}; got {entry['version']!r}"
        )
        if "expand" in exp:
            assert entry.get("expand") == exp["expand"], (
                f"Expected requests[{i}].expand == {exp['expand']!r} in {VALID_CONFIG}; got {entry.get('expand')!r}"
            )
        else:
            assert "expand" not in entry, (
                f"Expected requests[{i}] in {VALID_CONFIG} to omit the `expand` key entirely; got entry: {entry!r}"
            )


def test_llama_cloud_sdk_importable():
    """The llama_cloud SDK must be installed so the agent can import LlamaCloud."""
    result = subprocess.run(
        ["python3", "-c", "from llama_cloud import LlamaCloud; print('ok')"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        "Expected `from llama_cloud import LlamaCloud` to succeed but got: "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "ok" in result.stdout, (
        f"Expected import smoke test to print 'ok'; got stdout={result.stdout!r}"
    )


def test_pyyaml_importable():
    """PyYAML is required by the CLI to parse the manifest."""
    result = subprocess.run(
        ["python3", "-c", "import yaml; print(yaml.__version__)"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Expected `import yaml` to succeed but got: "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
