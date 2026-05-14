import os
import shutil
import subprocess

import yaml

PROJECT_DIR = "/home/user/composite_planner"
CONFIGS_DIR = os.path.join(PROJECT_DIR, "configs")
VALID_CONFIG = os.path.join(CONFIGS_DIR, "valid.yaml")


def test_python3_available():
    assert shutil.which("python3") is not None, (
        "python3 binary not found in PATH."
    )


def test_llama_cloud_sdk_importable():
    """The LlamaCloud SDK classes used by the task must be importable in the environment."""
    result = subprocess.run(
        [
            "python3",
            "-c",
            "from llama_index.indices.managed.llama_cloud import LlamaCloudCompositeRetriever\n"
            "from llama_cloud import CompositeRetrievalMode\n"
            "print('ok')\n",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        "Expected LlamaCloudCompositeRetriever and CompositeRetrievalMode to be "
        f"importable. stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "ok" in result.stdout, (
        f"Expected import probe to print 'ok'; got stdout={result.stdout!r}"
    )


def test_pyyaml_available():
    """PyYAML must be installed because the CLI must parse a YAML config."""
    result = subprocess.run(
        ["python3", "-c", "import yaml; print(yaml.__name__)"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"PyYAML import failed. stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "yaml" in result.stdout, (
        f"Expected `yaml` module name in stdout; got stdout={result.stdout!r}"
    )


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_configs_dir_exists():
    assert os.path.isdir(CONFIGS_DIR), (
        f"Configs directory {CONFIGS_DIR} does not exist."
    )


def test_valid_starter_config_exists():
    assert os.path.isfile(VALID_CONFIG), (
        f"Starter config {VALID_CONFIG} does not exist."
    )


def test_valid_starter_config_schema():
    """The starter config must exactly match the fixture contract stated in the task."""
    with open(VALID_CONFIG, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    assert isinstance(data, dict), (
        f"Starter config must be a YAML mapping; got {type(data).__name__}"
    )
    retriever = data.get("retriever")
    assert isinstance(retriever, dict), (
        f"`retriever` must be a mapping in {VALID_CONFIG}; got {retriever!r}"
    )
    assert retriever.get("name") == "Essays Retriever", (
        f"Expected retriever.name == 'Essays Retriever' in {VALID_CONFIG}; "
        f"got {retriever.get('name')!r}"
    )
    assert retriever.get("project_name") == "Essays", (
        f"Expected retriever.project_name == 'Essays' in {VALID_CONFIG}; "
        f"got {retriever.get('project_name')!r}"
    )
    assert retriever.get("mode") == "FULL", (
        f"Expected retriever.mode == 'FULL' in {VALID_CONFIG}; "
        f"got {retriever.get('mode')!r}"
    )
    assert retriever.get("rerank_top_n") == 5, (
        f"Expected retriever.rerank_top_n == 5 in {VALID_CONFIG}; "
        f"got {retriever.get('rerank_top_n')!r}"
    )
    assert retriever.get("create_if_not_exists") is True, (
        f"Expected retriever.create_if_not_exists == true in {VALID_CONFIG}; "
        f"got {retriever.get('create_if_not_exists')!r}"
    )

    sub_indices = data.get("sub_indices")
    assert isinstance(sub_indices, list) and len(sub_indices) == 2, (
        f"Expected sub_indices to be a list of length 2 in {VALID_CONFIG}; "
        f"got {sub_indices!r}"
    )

    first = sub_indices[0]
    assert first.get("name") == "slides_index", (
        f"Expected sub_indices[0].name == 'slides_index'; got {first!r}"
    )
    assert first.get("project_name") == "Essays", (
        f"Expected sub_indices[0].project_name == 'Essays'; got {first!r}"
    )
    assert (
        first.get("description")
        == "Information source for slide shows presented during team meetings"
    ), (
        "Expected sub_indices[0].description to match the slides description; "
        f"got {first!r}"
    )

    second = sub_indices[1]
    assert second.get("name") == "financial_index", (
        f"Expected sub_indices[1].name == 'financial_index'; got {second!r}"
    )
    assert second.get("project_name") == "Essays", (
        f"Expected sub_indices[1].project_name == 'Essays'; got {second!r}"
    )
    assert (
        second.get("description")
        == "Information source for company financial reports"
    ), (
        "Expected sub_indices[1].description to match the financial description; "
        f"got {second!r}"
    )
