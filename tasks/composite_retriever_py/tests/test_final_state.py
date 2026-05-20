import os
import re
import subprocess

import pytest
import requests

PROJECT_DIR = "/home/user/myproject"
SCRIPT_PATH = os.path.join(PROJECT_DIR, "run_retrieval.py")
LOG_PATH = os.path.join(PROJECT_DIR, "retrieval.log")
TRIAL_ID_PATH = "/logs/artifacts/trial_id"

BASE_URL = os.environ.get("LLAMA_CLOUD_BASE_URL", "https://api.cloud.llamaindex.ai").rstrip("/")
API_KEY = os.environ.get("LLAMA_CLOUD_API_KEY", "")
PROJECT_NAME = os.environ.get("LLAMA_CLOUD_PROJECT_NAME", "Default")

FAQ_QUERY = "How do I reset my password?"
PRODUCT_QUERY = "What is the maximum payload size of the streaming API?"


def _read_trial_id() -> str:
    with open(TRIAL_ID_PATH) as f:
        return f.read().strip()


def _auth_headers():
    return {"Authorization": f"Bearer {API_KEY}"}


def _list_pipelines():
    resp = requests.get(
        f"{BASE_URL}/api/v1/pipelines",
        headers=_auth_headers(),
        params={"project_name": PROJECT_NAME},
        timeout=60,
    )
    assert resp.status_code == 200, (
        f"Listing pipelines failed: status={resp.status_code}, body={resp.text}"
    )
    return resp.json()


def _list_retrievers():
    resp = requests.get(
        f"{BASE_URL}/api/v1/retrievers",
        headers=_auth_headers(),
        params={"project_name": PROJECT_NAME},
        timeout=60,
    )
    assert resp.status_code == 200, (
        f"Listing retrievers failed: status={resp.status_code}, body={resp.text}"
    )
    return resp.json()


@pytest.fixture(scope="session")
def trial_id():
    assert os.path.isfile(TRIAL_ID_PATH), f"trial_id file missing at {TRIAL_ID_PATH}"
    tid = _read_trial_id()
    assert tid, "trial_id file is empty."
    return tid


@pytest.fixture(scope="session")
def cleaned_log():
    if os.path.isfile(LOG_PATH):
        os.remove(LOG_PATH)


@pytest.fixture(scope="session")
def faq_run(cleaned_log, trial_id):
    """Run the FAQ query and capture stdout."""
    result = subprocess.run(
        ["python3", SCRIPT_PATH, "--query", FAQ_QUERY],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert result.returncode == 0, (
        f"run_retrieval.py exited with non-zero for FAQ query.\n"
        f"stdout=\n{result.stdout}\nstderr=\n{result.stderr}"
    )
    return result


@pytest.fixture(scope="session")
def product_run(faq_run, trial_id):
    """Run the product query after the FAQ query and capture stdout."""
    result = subprocess.run(
        ["python3", SCRIPT_PATH, "--query", PRODUCT_QUERY],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert result.returncode == 0, (
        f"run_retrieval.py exited with non-zero for product query.\n"
        f"stdout=\n{result.stdout}\nstderr=\n{result.stderr}"
    )
    return result


def test_script_file_exists():
    assert os.path.isfile(SCRIPT_PATH), f"Expected the executor to create {SCRIPT_PATH}."


def test_product_pipeline_exists_on_llamacloud(faq_run, trial_id):
    expected_name = f"product-docs-{trial_id}"
    pipelines = _list_pipelines()
    names = [p.get("name") for p in pipelines]
    assert expected_name in names, (
        f"Expected LlamaCloud pipeline '{expected_name}' to exist in project "
        f"'{PROJECT_NAME}'. Found pipelines: {names}"
    )


def test_faq_pipeline_exists_on_llamacloud(faq_run, trial_id):
    expected_name = f"faq-docs-{trial_id}"
    pipelines = _list_pipelines()
    names = [p.get("name") for p in pipelines]
    assert expected_name in names, (
        f"Expected LlamaCloud pipeline '{expected_name}' to exist in project "
        f"'{PROJECT_NAME}'. Found pipelines: {names}"
    )


def test_composite_retriever_exists_with_full_mode(faq_run, trial_id):
    expected_name = f"support-composite-{trial_id}"
    retrievers = _list_retrievers()
    matching = [r for r in retrievers if r.get("name") == expected_name]
    assert matching, (
        f"Expected LlamaCloud retriever '{expected_name}' to exist in project "
        f"'{PROJECT_NAME}'. Found retrievers: {[r.get('name') for r in retrievers]}"
    )
    retriever = matching[0]
    # Retrievers in LlamaCloud expose a `pipelines` array of attached sub-indices.
    attached_pipeline_names = []
    for pl in retriever.get("pipelines") or []:
        if isinstance(pl, dict):
            attached_pipeline_names.append(pl.get("name") or pl.get("pipeline_name"))
    attached_pipeline_names = [n for n in attached_pipeline_names if n]
    assert f"product-docs-{trial_id}" in attached_pipeline_names, (
        f"Expected composite retriever to be linked to 'product-docs-{trial_id}'. "
        f"Linked pipelines: {attached_pipeline_names}"
    )
    assert f"faq-docs-{trial_id}" in attached_pipeline_names, (
        f"Expected composite retriever to be linked to 'faq-docs-{trial_id}'. "
        f"Linked pipelines: {attached_pipeline_names}"
    )
    mode_value = retriever.get("mode") or retriever.get("retrieval_mode") or ""
    assert str(mode_value).upper().endswith("FULL"), (
        f"Expected composite retriever mode to be 'FULL', got '{mode_value}'."
    )


def test_faq_run_log_contains_faq_hit(faq_run, trial_id):
    assert os.path.isfile(LOG_PATH), f"Expected log file at {LOG_PATH} after running the FAQ query."
    with open(LOG_PATH) as f:
        log_content = f.read()
    pattern = re.compile(
        rf"^INDEX=faq-docs-{re.escape(trial_id)} \| SCORE=[0-9eE+\-.]+ \| TEXT=.+$",
        re.MULTILINE,
    )
    assert pattern.search(log_content), (
        f"Expected at least one line in {LOG_PATH} matching 'INDEX=faq-docs-{trial_id} | SCORE=... | TEXT=...' "
        f"for the FAQ query.\nLog content:\n{log_content}"
    )
    assert re.search(r"^Retrieved \d+ nodes$", log_content, re.MULTILINE), (
        "Expected the log file to contain a final 'Retrieved <n> nodes' line."
    )


def test_faq_run_stdout_matches_log(faq_run, trial_id):
    stdout = faq_run.stdout
    pattern = re.compile(
        rf"INDEX=faq-docs-{re.escape(trial_id)} \| SCORE=[0-9eE+\-.]+ \| TEXT=",
    )
    assert pattern.search(stdout), (
        f"Expected stdout from the FAQ query to contain a line with "
        f"'INDEX=faq-docs-{trial_id} | SCORE=... | TEXT=...'.\nGot stdout:\n{stdout}"
    )
    assert re.search(r"Retrieved \d+ nodes", stdout), (
        f"Expected stdout to include 'Retrieved <n> nodes'.\nGot stdout:\n{stdout}"
    )


def test_product_run_log_contains_product_hit(product_run, trial_id):
    assert os.path.isfile(LOG_PATH), f"Expected log file at {LOG_PATH} after running the product query."
    with open(LOG_PATH) as f:
        log_content = f.read()
    pattern = re.compile(
        rf"^INDEX=product-docs-{re.escape(trial_id)} \| SCORE=[0-9eE+\-.]+ \| TEXT=.+$",
        re.MULTILINE,
    )
    assert pattern.search(log_content), (
        f"Expected at least one line in {LOG_PATH} matching "
        f"'INDEX=product-docs-{trial_id} | SCORE=... | TEXT=...' for the product query.\n"
        f"Log content:\n{log_content}"
    )


def test_product_run_stdout_matches_log(product_run, trial_id):
    stdout = product_run.stdout
    pattern = re.compile(
        rf"INDEX=product-docs-{re.escape(trial_id)} \| SCORE=[0-9eE+\-.]+ \| TEXT=",
    )
    assert pattern.search(stdout), (
        f"Expected stdout from the product query to contain a line with "
        f"'INDEX=product-docs-{trial_id} | SCORE=... | TEXT=...'.\nGot stdout:\n{stdout}"
    )
    assert re.search(r"Retrieved \d+ nodes", stdout), (
        f"Expected stdout to include 'Retrieved <n> nodes'.\nGot stdout:\n{stdout}"
    )
