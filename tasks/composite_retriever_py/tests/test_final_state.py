import os
import subprocess

import pytest
import requests

PROJECT_DIR = "/home/user/myproject"
SCRIPT_PATH = os.path.join(PROJECT_DIR, "composite.py")
PRODUCTS_DIR = os.path.join(PROJECT_DIR, "products")
SUPPORT_DIR = os.path.join(PROJECT_DIR, "support")
OUTPUT_FILE = os.path.join(PROJECT_DIR, "nodes.txt")
TRIAL_ID_FILE = "/logs/artifacts/trial_id"
LLAMA_CLOUD_BASE_URL = "https://api.cloud.llamaindex.ai"
QUERY = "What is the maximum operating temperature of the Model X100 widget?"


def _read_trial_id():
    with open(TRIAL_ID_FILE, "r", encoding="utf-8") as f:
        return f.read().strip()


def _products_index_name():
    return f"harbor-products-{_read_trial_id()}"


def _support_index_name():
    return f"harbor-support-{_read_trial_id()}"


def _composite_retriever_name():
    return f"harbor-composite-{_read_trial_id()}"


def _llama_cloud_headers():
    api_key = os.environ.get("LLAMA_CLOUD_API_KEY")
    assert api_key, "LLAMA_CLOUD_API_KEY env var is required for verification."
    return {"Authorization": f"Bearer {api_key}"}


@pytest.fixture(scope="module")
def run_script():
    """Run the user's script once for the entire module and return the result."""
    if os.path.isfile(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)

    assert os.path.isfile(SCRIPT_PATH), (
        f"Expected user-provided script at {SCRIPT_PATH}; it was not found."
    )

    result = subprocess.run(
        [
            "python3",
            "composite.py",
            "--products-dir",
            PRODUCTS_DIR,
            "--support-dir",
            SUPPORT_DIR,
            "--query",
            QUERY,
            "--output",
            OUTPUT_FILE,
        ],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
        timeout=900,
    )
    return result


def test_script_exits_zero(run_script):
    assert run_script.returncode == 0, (
        "Expected composite.py to exit with code 0, "
        f"got {run_script.returncode}. stdout={run_script.stdout!r} "
        f"stderr={run_script.stderr!r}"
    )


def test_stdout_contains_retriever_name(run_script):
    expected_line = f"Retriever name: {_composite_retriever_name()}"
    stdout_lines = [line.strip() for line in run_script.stdout.splitlines()]
    assert expected_line in stdout_lines, (
        f"Expected stdout to contain the line {expected_line!r}, "
        f"got stdout lines: {stdout_lines!r}"
    )


@pytest.fixture(scope="module")
def pipeline_ids(run_script):
    """Fetch the pipeline ids for the two managed indexes created by the script."""
    response = requests.get(
        f"{LLAMA_CLOUD_BASE_URL}/api/v1/pipelines",
        headers=_llama_cloud_headers(),
        params={"project_name": "Default"},
        timeout=60,
    )
    assert response.status_code == 200, (
        f"LlamaCloud pipelines list returned status "
        f"{response.status_code}: {response.text}"
    )
    pipelines = response.json()
    assert isinstance(pipelines, list), (
        f"Expected pipelines list response to be a JSON array, got: {pipelines!r}"
    )
    by_name = {p.get("name"): p.get("id") for p in pipelines}

    products_name = _products_index_name()
    support_name = _support_index_name()

    assert products_name in by_name, (
        f"Expected pipeline {products_name!r} to exist in LlamaCloud project "
        f"'Default'; got names={sorted(by_name.keys())!r}"
    )
    assert support_name in by_name, (
        f"Expected pipeline {support_name!r} to exist in LlamaCloud project "
        f"'Default'; got names={sorted(by_name.keys())!r}"
    )

    return {
        "products": by_name[products_name],
        "support": by_name[support_name],
    }


def test_products_index_exists_on_llamacloud(pipeline_ids):
    """Both managed indexes must exist on LlamaCloud (fixture asserts presence)."""
    assert pipeline_ids["products"], "Products pipeline id is missing."


def test_support_index_exists_on_llamacloud(pipeline_ids):
    """Both managed indexes must exist on LlamaCloud (fixture asserts presence)."""
    assert pipeline_ids["support"], "Support pipeline id is missing."


def test_composite_retriever_exists_with_two_pipelines(pipeline_ids):
    """Verify the composite retriever exists and references both pipelines."""
    expected_name = _composite_retriever_name()
    response = requests.get(
        f"{LLAMA_CLOUD_BASE_URL}/api/v1/retrievers",
        headers=_llama_cloud_headers(),
        params={"name": expected_name},
        timeout=60,
    )
    assert response.status_code == 200, (
        f"LlamaCloud retrievers list returned status "
        f"{response.status_code}: {response.text}"
    )
    retrievers = response.json()
    assert isinstance(retrievers, list), (
        f"Expected retrievers list response to be a JSON array, got: {retrievers!r}"
    )
    matching = [r for r in retrievers if r.get("name") == expected_name]
    assert matching, (
        f"Expected at least one retriever with name {expected_name!r}; "
        f"got names={[r.get('name') for r in retrievers]!r}"
    )

    retriever = matching[0]
    pipelines = retriever.get("pipelines") or []
    assert len(pipelines) == 2, (
        f"Expected composite retriever {expected_name!r} to have exactly 2 "
        f"attached pipelines; got {len(pipelines)} entries: {pipelines!r}"
    )

    attached_ids = {p.get("pipeline_id") for p in pipelines}
    expected_ids = {pipeline_ids["products"], pipeline_ids["support"]}
    assert attached_ids == expected_ids, (
        f"Expected composite retriever {expected_name!r} to reference pipeline "
        f"ids {expected_ids!r}; got {attached_ids!r}"
    )


def test_output_file_exists_and_non_empty(run_script):
    assert os.path.isfile(OUTPUT_FILE), (
        f"Expected output file {OUTPUT_FILE} to be created by composite.py."
    )
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    assert content.strip(), (
        f"Output file {OUTPUT_FILE} exists but is empty; expected at least one retrieved node."
    )


def test_output_file_lines_start_with_score(run_script):
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        lines = [line for line in f.read().splitlines() if line.strip()]
    assert lines, (
        f"Output file {OUTPUT_FILE} contains no non-empty lines."
    )
    for line in lines:
        assert line.startswith("score="), (
            f"Every non-empty line in {OUTPUT_FILE} must start with 'score='. "
            f"Offending line: {line!r}"
        )


def test_output_file_contains_temperature_answer(run_script):
    """The Model X100 specs (175 degrees) should appear in the retrieved chunks."""
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    assert "175" in content, (
        "Expected the retrieved chunks to mention the answer '175'. "
        f"Actual content: {content!r}"
    )


def test_script_imports_and_calls():
    with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
        source = f.read()
    assert "llama_index.indices.managed.llama_cloud" in source, (
        "composite.py must reference the llama_index.indices.managed.llama_cloud module."
    )
    assert "LlamaCloudIndex" in source, (
        "composite.py must use LlamaCloudIndex."
    )
    assert "LlamaCloudCompositeRetriever" in source, (
        "composite.py must use LlamaCloudCompositeRetriever."
    )
    assert "from llama_cloud import" in source and "CompositeRetrievalMode" in source, (
        "composite.py must import CompositeRetrievalMode from the llama_cloud package."
    )
    assert "LlamaCloudIndex.from_documents" in source, (
        "composite.py must call LlamaCloudIndex.from_documents to create each managed index."
    )
    assert (
        'project_name="Default"' in source or "project_name='Default'" in source
    ), (
        "composite.py must pass project_name=\"Default\" to LlamaCloudIndex.from_documents."
    )
    assert "CompositeRetrievalMode.FULL" in source, (
        "composite.py must use CompositeRetrievalMode.FULL for the composite retriever."
    )
    assert "rerank_top_n=5" in source, (
        "composite.py must pass rerank_top_n=5 to the composite retriever constructor."
    )
    assert source.count(".add_index(") >= 2, (
        "composite.py must call composite_retriever.add_index at least twice "
        "(once per managed index)."
    )
    assert "/logs/artifacts/trial_id" in source, (
        "composite.py must read the trial_id from /logs/artifacts/trial_id."
    )


def test_script_fails_on_missing_products_dir():
    """The script must exit non-zero when --products-dir does not exist."""
    missing_dir = os.path.join(PROJECT_DIR, "does_not_exist_products_dir")
    assert not os.path.exists(missing_dir), (
        f"Test prerequisite failed: {missing_dir} should not exist."
    )
    result = subprocess.run(
        [
            "python3",
            "composite.py",
            "--products-dir",
            missing_dir,
            "--support-dir",
            SUPPORT_DIR,
            "--query",
            "anything",
            "--output",
            os.path.join(PROJECT_DIR, "should_not_be_written.txt"),
        ],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
        timeout=120,
    )
    assert result.returncode != 0, (
        "Expected composite.py to exit with a non-zero status code when "
        f"--products-dir does not exist; got returncode={result.returncode}, "
        f"stdout={result.stdout!r}, stderr={result.stderr!r}"
    )


def test_script_fails_on_missing_support_dir():
    """The script must exit non-zero when --support-dir does not exist."""
    missing_dir = os.path.join(PROJECT_DIR, "does_not_exist_support_dir")
    assert not os.path.exists(missing_dir), (
        f"Test prerequisite failed: {missing_dir} should not exist."
    )
    result = subprocess.run(
        [
            "python3",
            "composite.py",
            "--products-dir",
            PRODUCTS_DIR,
            "--support-dir",
            missing_dir,
            "--query",
            "anything",
            "--output",
            os.path.join(PROJECT_DIR, "should_not_be_written.txt"),
        ],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
        timeout=120,
    )
    assert result.returncode != 0, (
        "Expected composite.py to exit with a non-zero status code when "
        f"--support-dir does not exist; got returncode={result.returncode}, "
        f"stdout={result.stdout!r}, stderr={result.stderr!r}"
    )
