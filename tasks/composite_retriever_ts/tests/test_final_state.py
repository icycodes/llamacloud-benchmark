import os
import re

import pytest
import requests

PROJECT_DIR = "/home/user/composite_retriever"
LOG_PATH = os.path.join(PROJECT_DIR, "output.log")
TRIAL_ID_PATH = "/logs/artifacts/trial_id"

LLAMA_CLOUD_BASE_URL = os.environ.get(
    "LLAMA_CLOUD_BASE_URL", "https://api.cloud.llamaindex.ai"
).rstrip("/")


def _trial_id() -> str:
    with open(TRIAL_ID_PATH) as f:
        value = f.read().strip()
    assert value, f"Trial id file {TRIAL_ID_PATH} is empty."
    return value


def _auth_headers() -> dict:
    api_key = os.environ.get("LLAMA_CLOUD_API_KEY")
    assert api_key, "LLAMA_CLOUD_API_KEY must be set for verification."
    return {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }


def _read_log() -> str:
    assert os.path.isfile(LOG_PATH), f"Expected log file at {LOG_PATH}."
    with open(LOG_PATH) as f:
        return f.read()


def _list_pipelines() -> list:
    resp = requests.get(
        f"{LLAMA_CLOUD_BASE_URL}/api/v1/pipelines",
        headers=_auth_headers(),
        timeout=60,
    )
    assert resp.status_code == 200, (
        f"Failed to list pipelines (status {resp.status_code}): {resp.text}"
    )
    data = resp.json()
    if isinstance(data, dict) and "data" in data:
        return data["data"]
    return data


def _list_retrievers() -> list:
    resp = requests.get(
        f"{LLAMA_CLOUD_BASE_URL}/api/v1/retrievers",
        headers=_auth_headers(),
        timeout=60,
    )
    assert resp.status_code == 200, (
        f"Failed to list retrievers (status {resp.status_code}): {resp.text}"
    )
    data = resp.json()
    if isinstance(data, dict) and "data" in data:
        return data["data"]
    return data


@pytest.fixture(scope="module")
def trial_id() -> str:
    return _trial_id()


@pytest.fixture(scope="module")
def log_text() -> str:
    return _read_log()


@pytest.fixture(scope="module")
def expected_names(trial_id):
    return {
        "policies": f"policies-{trial_id}",
        "faq": f"faq-{trial_id}",
        "retriever": f"composite-retriever-{trial_id}",
    }


def test_log_contains_trial_id(log_text, trial_id):
    assert re.search(rf"^Trial ID:\s*{re.escape(trial_id)}\s*$", log_text, re.MULTILINE), (
        f"Log file must contain a 'Trial ID: {trial_id}' line."
    )


def test_log_contains_pipeline_ids(log_text):
    assert re.search(
        r"^Policies Pipeline ID:\s*[A-Za-z0-9\-]+\s*$", log_text, re.MULTILINE
    ), "Log file must contain a 'Policies Pipeline ID: <id>' line."
    assert re.search(
        r"^FAQ Pipeline ID:\s*[A-Za-z0-9\-]+\s*$", log_text, re.MULTILINE
    ), "Log file must contain a 'FAQ Pipeline ID: <id>' line."


def test_log_contains_retriever_id(log_text):
    assert re.search(
        r"^Composite Retriever ID:\s*[A-Za-z0-9\-]+\s*$", log_text, re.MULTILINE
    ), "Log file must contain a 'Composite Retriever ID: <id>' line."


def test_log_contains_query(log_text):
    match = re.search(r"^Query:\s*(.+?)\s*$", log_text, re.MULTILINE)
    assert match, "Log file must contain a 'Query: <query>' line."
    assert match.group(1).strip(), "The 'Query:' line must not be empty."


def test_log_contains_result_count(log_text):
    match = re.search(r"^Result Count:\s*(\d+)\s*$", log_text, re.MULTILINE)
    assert match, "Log file must contain a 'Result Count: <n>' line."
    count = int(match.group(1))
    assert count >= 1, f"Result Count must be >= 1, got {count}."


def test_log_contains_node_score_lines(log_text):
    matches = re.findall(
        r"^Node Score:\s*[-+0-9.eE]+\s*\|\s*Text:\s*.+$", log_text, re.MULTILINE
    )
    assert len(matches) >= 1, (
        "Log file must contain at least one 'Node Score: <score> | Text: <text>' line."
    )


def test_pipelines_exist_in_llama_cloud(expected_names):
    pipelines = _list_pipelines()
    names = {p.get("name") for p in pipelines}
    assert expected_names["policies"] in names, (
        f"Expected LlamaCloud pipeline '{expected_names['policies']}' was not found. "
        f"Existing names sample: {list(names)[:20]}"
    )
    assert expected_names["faq"] in names, (
        f"Expected LlamaCloud pipeline '{expected_names['faq']}' was not found. "
        f"Existing names sample: {list(names)[:20]}"
    )


def test_pipeline_ids_match_log(log_text, expected_names):
    pipelines = _list_pipelines()
    by_name = {p.get("name"): p.get("id") for p in pipelines}

    policies_log_match = re.search(
        r"^Policies Pipeline ID:\s*([A-Za-z0-9\-]+)\s*$", log_text, re.MULTILINE
    )
    faq_log_match = re.search(
        r"^FAQ Pipeline ID:\s*([A-Za-z0-9\-]+)\s*$", log_text, re.MULTILINE
    )
    assert policies_log_match and faq_log_match, (
        "Log file must contain both 'Policies Pipeline ID' and 'FAQ Pipeline ID' lines."
    )

    policies_logged_id = policies_log_match.group(1)
    faq_logged_id = faq_log_match.group(1)

    assert by_name.get(expected_names["policies"]) == policies_logged_id, (
        f"Policies pipeline ID in log ({policies_logged_id}) does not match the LlamaCloud "
        f"pipeline ID for '{expected_names['policies']}' ({by_name.get(expected_names['policies'])})."
    )
    assert by_name.get(expected_names["faq"]) == faq_logged_id, (
        f"FAQ pipeline ID in log ({faq_logged_id}) does not match the LlamaCloud "
        f"pipeline ID for '{expected_names['faq']}' ({by_name.get(expected_names['faq'])})."
    )


def test_retriever_exists_and_references_both_pipelines(log_text, expected_names):
    retrievers = _list_retrievers()
    matching = [r for r in retrievers if r.get("name") == expected_names["retriever"]]
    assert matching, (
        f"Expected LlamaCloud retriever '{expected_names['retriever']}' was not found."
    )
    retriever = matching[0]

    log_id_match = re.search(
        r"^Composite Retriever ID:\s*([A-Za-z0-9\-]+)\s*$", log_text, re.MULTILINE
    )
    assert log_id_match, "Log file must contain a 'Composite Retriever ID: <id>' line."
    assert retriever.get("id") == log_id_match.group(1), (
        f"Composite Retriever ID in log ({log_id_match.group(1)}) does not match "
        f"the LlamaCloud retriever ID ({retriever.get('id')})."
    )

    pipelines = _list_pipelines()
    by_name = {p.get("name"): p.get("id") for p in pipelines}
    expected_pipeline_ids = {
        by_name.get(expected_names["policies"]),
        by_name.get(expected_names["faq"]),
    }
    referenced_ids = set()
    for sub in retriever.get("pipelines", []) or []:
        if isinstance(sub, dict):
            referenced_ids.add(sub.get("pipeline_id") or sub.get("id"))
    assert expected_pipeline_ids.issubset(referenced_ids), (
        f"Composite retriever must reference both pipeline IDs {expected_pipeline_ids}, "
        f"but it references {referenced_ids}."
    )


def test_retriever_returns_nodes_on_search(expected_names):
    retrievers = _list_retrievers()
    matching = [r for r in retrievers if r.get("name") == expected_names["retriever"]]
    assert matching, (
        f"Expected LlamaCloud retriever '{expected_names['retriever']}' was not found."
    )
    retriever_id = matching[0]["id"]

    resp = requests.post(
        f"{LLAMA_CLOUD_BASE_URL}/api/v1/retrievers/{retriever_id}/retrieve",
        headers={**_auth_headers(), "Content-Type": "application/json"},
        json={
            "query": "What is the company refund policy?",
            "mode": "full",
            "rerank_top_n": 5,
        },
        timeout=120,
    )
    assert resp.status_code == 200, (
        f"Retriever search failed (status {resp.status_code}): {resp.text}"
    )
    data = resp.json()
    nodes = data.get("nodes") or data.get("retrieval_nodes") or []
    assert isinstance(nodes, list) and len(nodes) >= 1, (
        f"Composite retriever search returned no nodes. Response: {data}"
    )
