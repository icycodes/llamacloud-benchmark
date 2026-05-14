import os
import shutil
import yaml
import pytest

PROJECT_DIR = "/home/user/mcp_config_builder"
CONFIGS_DIR = os.path.join(PROJECT_DIR, "configs")
VALID_YAML = os.path.join(CONFIGS_DIR, "valid.yaml")


def test_python3_available():
    assert shutil.which("python3") is not None, "python3 binary not found in PATH."


def test_llama_cloud_sdk_importable():
    """The LlamaCloud Python SDK must be importable in the task environment."""
    try:
        from llama_cloud.client import LlamaCloud  # noqa: F401
    except Exception as exc:
        pytest.fail(
            f"Failed to import LlamaCloud from llama_cloud.client: {exc!r}. "
            "The llama-cloud SDK must be pre-installed in the environment."
        )


def test_pyyaml_available():
    """pyyaml must be importable for the task's config parsing."""
    try:
        import yaml  # noqa: F401
    except Exception as exc:
        pytest.fail(f"Failed to import yaml (pyyaml): {exc!r}.")


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_configs_directory_exists():
    assert os.path.isdir(CONFIGS_DIR), (
        f"Configs directory {CONFIGS_DIR} does not exist."
    )


def test_valid_yaml_fixture_exists():
    assert os.path.isfile(VALID_YAML), (
        f"Starter fixture {VALID_YAML} does not exist."
    )


def test_valid_yaml_fixture_contents():
    """The starter YAML must contain the expected server_name, project_name, and indices."""
    with open(VALID_YAML, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    assert isinstance(data, dict), (
        f"Starter fixture {VALID_YAML} must parse to a dict, got {type(data).__name__}."
    )
    assert data.get("server_name") == "llamacloud", (
        f"Expected server_name=='llamacloud' in {VALID_YAML}, got {data.get('server_name')!r}."
    )
    assert data.get("project_name") == "Financials", (
        f"Expected project_name=='Financials' in {VALID_YAML}, got {data.get('project_name')!r}."
    )

    indices = data.get("indices")
    assert isinstance(indices, list) and len(indices) == 2, (
        f"Expected indices to be a list of length 2 in {VALID_YAML}, got {indices!r}."
    )

    first = indices[0]
    assert first.get("name") == "10k-SEC-Tesla", (
        f"Expected first index name=='10k-SEC-Tesla', got {first.get('name')!r}."
    )
    assert first.get("description") == "10k SEC documents from 2023 for Tesla", (
        f"Expected first index description=='10k SEC documents from 2023 for Tesla', "
        f"got {first.get('description')!r}."
    )
    assert first.get("top_k") == 5, (
        f"Expected first index top_k==5, got {first.get('top_k')!r}."
    )

    second = indices[1]
    assert second.get("name") == "10k-SEC-Apple", (
        f"Expected second index name=='10k-SEC-Apple', got {second.get('name')!r}."
    )
    assert second.get("description") == "10k SEC documents from 2023 for Apple", (
        f"Expected second index description=='10k SEC documents from 2023 for Apple', "
        f"got {second.get('description')!r}."
    )
    assert "top_k" not in second, (
        f"Expected second index to omit top_k, but found top_k={second.get('top_k')!r}."
    )


def test_build_script_not_yet_created():
    """The build script is what the user must produce; it must not be pre-supplied."""
    script_path = os.path.join(PROJECT_DIR, "build_mcp_config.py")
    assert not os.path.exists(script_path), (
        f"{script_path} must not exist before the task starts; it is the user's deliverable."
    )
