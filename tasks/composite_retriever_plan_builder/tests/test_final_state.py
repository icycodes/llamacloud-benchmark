import json
import os
import subprocess

import pytest

PROJECT_DIR = "/home/user/composite_planner"
CONFIGS_DIR = os.path.join(PROJECT_DIR, "configs")
SCRIPT_PATH = os.path.join(PROJECT_DIR, "build_plan.py")

VALID_CONFIG = os.path.join(CONFIGS_DIR, "valid.yaml")
ROUTING_CONFIG = os.path.join(CONFIGS_DIR, "routing.yaml")
MISSING_DESC_CONFIG = os.path.join(CONFIGS_DIR, "missing_desc.yaml")
NO_SUCH_CONFIG = os.path.join(CONFIGS_DIR, "no_such_file.yaml")

PLAN_OUT = os.path.join(PROJECT_DIR, "plan.json")
ROUTING_OUT = os.path.join(PROJECT_DIR, "routing_plan.json")
BAD_OUT = os.path.join(PROJECT_DIR, "bad_plan.json")
SHOULD_NOT_EXIST_OUT = os.path.join(PROJECT_DIR, "should_not_exist.json")


@pytest.fixture(autouse=True)
def cleanup_outputs():
    """Remove any stale output files before each verification test."""
    for path in (PLAN_OUT, ROUTING_OUT, BAD_OUT, SHOULD_NOT_EXIST_OUT):
        if os.path.exists(path):
            os.remove(path)
    yield


def test_script_exists():
    assert os.path.isfile(SCRIPT_PATH), (
        f"Expected the CLI script to exist at {SCRIPT_PATH}."
    )


def test_script_imports_sdk_classes():
    with open(SCRIPT_PATH, "r", encoding="utf-8") as fh:
        contents = fh.read()
    assert (
        "from llama_index.indices.managed.llama_cloud import LlamaCloudCompositeRetriever"
        in contents
    ), (
        "Script must import LlamaCloudCompositeRetriever from "
        "llama_index.indices.managed.llama_cloud (verbatim).\n"
        f"Current contents:\n{contents}"
    )
    assert "from llama_cloud import CompositeRetrievalMode" in contents, (
        "Script must import CompositeRetrievalMode from llama_cloud (verbatim).\n"
        f"Current contents:\n{contents}"
    )


def test_full_mode_happy_path_run():
    result = subprocess.run(
        [
            "python3",
            SCRIPT_PATH,
            "--config",
            VALID_CONFIG,
            "--output",
            PLAN_OUT,
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Happy-path FULL run should exit 0 but exited {result.returncode}. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    expected_stdout_line = (
        f"Composite retriever plan written to {PLAN_OUT}: "
        "name=Essays Retriever mode=FULL sub_indices=2"
    )
    assert expected_stdout_line in result.stdout, (
        f"Expected stdout to contain {expected_stdout_line!r}; "
        f"got stdout={result.stdout!r}"
    )

    assert os.path.isfile(PLAN_OUT), (
        f"Expected plan file {PLAN_OUT} to be created."
    )
    with open(PLAN_OUT, "r", encoding="utf-8") as fh:
        plan = json.load(fh)

    assert set(plan.keys()) == {"retriever", "sub_indices", "summary"}, (
        f"Expected plan top-level keys to be exactly {{retriever, sub_indices, "
        f"summary}}; got {sorted(plan.keys())!r}"
    )

    expected_retriever = {
        "name": "Essays Retriever",
        "project_name": "Essays",
        "mode": "FULL",
        "rerank_top_n": 5,
        "create_if_not_exists": True,
    }
    assert plan["retriever"] == expected_retriever, (
        f"Expected plan['retriever']=={expected_retriever!r}; "
        f"got {plan['retriever']!r}"
    )

    assert isinstance(plan["sub_indices"], list) and len(plan["sub_indices"]) == 2, (
        f"Expected plan['sub_indices'] to be a list of length 2; "
        f"got {plan['sub_indices']!r}"
    )
    assert plan["sub_indices"][0] == {
        "name": "slides_index",
        "project_name": "Essays",
        "description": (
            "Information source for slide shows presented during team meetings"
        ),
    }, (
        f"Expected first sub_index entry to be slides_index in original order; "
        f"got {plan['sub_indices'][0]!r}"
    )
    assert plan["sub_indices"][1] == {
        "name": "financial_index",
        "project_name": "Essays",
        "description": "Information source for company financial reports",
    }, (
        f"Expected second sub_index entry to be financial_index in original order; "
        f"got {plan['sub_indices'][1]!r}"
    )

    assert plan["summary"] == {"sub_index_count": 2, "mode": "FULL"}, (
        f"Expected plan['summary'] == {{'sub_index_count': 2, 'mode': 'FULL'}}; "
        f"got {plan['summary']!r}"
    )


def test_routing_mode_run_normalises_to_uppercase():
    assert os.path.isfile(ROUTING_CONFIG), (
        f"Expected the routing-mode config to exist at {ROUTING_CONFIG}. "
        "The task description requires the user to create it."
    )

    result = subprocess.run(
        [
            "python3",
            SCRIPT_PATH,
            "--config",
            ROUTING_CONFIG,
            "--output",
            ROUTING_OUT,
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Routing-mode run should exit 0 but exited {result.returncode}. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    expected_stdout_line = (
        f"Composite retriever plan written to {ROUTING_OUT}: "
        "name=Routing Retriever mode=ROUTING sub_indices=2"
    )
    assert expected_stdout_line in result.stdout, (
        f"Expected stdout to contain {expected_stdout_line!r}; "
        f"got stdout={result.stdout!r}"
    )

    assert os.path.isfile(ROUTING_OUT), (
        f"Expected routing plan file {ROUTING_OUT} to be created."
    )
    with open(ROUTING_OUT, "r", encoding="utf-8") as fh:
        plan = json.load(fh)

    assert plan["retriever"]["mode"] == "ROUTING", (
        f"Expected normalised mode == 'ROUTING'; got {plan['retriever']!r}"
    )
    assert plan["retriever"]["rerank_top_n"] == 3, (
        f"Expected retriever.rerank_top_n == 3; got {plan['retriever']!r}"
    )
    assert plan["retriever"]["create_if_not_exists"] is False, (
        f"Expected retriever.create_if_not_exists == false; got {plan['retriever']!r}"
    )
    assert plan["summary"] == {"sub_index_count": 2, "mode": "ROUTING"}, (
        f"Expected summary == {{'sub_index_count': 2, 'mode': 'ROUTING'}}; "
        f"got {plan['summary']!r}"
    )


def test_validation_error_for_empty_description():
    assert os.path.isfile(MISSING_DESC_CONFIG), (
        f"Expected the missing-description config at {MISSING_DESC_CONFIG}. "
        "The task description requires the user to create it."
    )

    result = subprocess.run(
        [
            "python3",
            SCRIPT_PATH,
            "--config",
            MISSING_DESC_CONFIG,
            "--output",
            BAD_OUT,
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0, (
        "Empty-description validation should exit non-zero but exited "
        f"{result.returncode}. stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    expected_error = (
        "Error: sub_indices[1].description must be a non-empty string"
    )
    assert expected_error in result.stderr, (
        f"Expected stderr to contain {expected_error!r}; "
        f"got stderr={result.stderr!r}"
    )
    assert not os.path.exists(BAD_OUT), (
        f"Output file {BAD_OUT} must NOT be created on validation failure."
    )


def test_validation_error_for_missing_config_file():
    result = subprocess.run(
        [
            "python3",
            SCRIPT_PATH,
            "--config",
            NO_SUCH_CONFIG,
            "--output",
            SHOULD_NOT_EXIST_OUT,
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0, (
        "Missing-config-file validation should exit non-zero but exited "
        f"{result.returncode}. stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    expected_error = f"Error: config file not found: {NO_SUCH_CONFIG}"
    assert expected_error in result.stderr, (
        f"Expected stderr to contain {expected_error!r}; "
        f"got stderr={result.stderr!r}"
    )
    assert not os.path.exists(SHOULD_NOT_EXIST_OUT), (
        f"Output file {SHOULD_NOT_EXIST_OUT} must NOT be created on validation failure."
    )
