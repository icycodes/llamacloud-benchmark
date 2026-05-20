import os
import re

import pytest

PROJECT_DIR = "/home/user/myproject"
LOG_FILE = os.path.join(PROJECT_DIR, "output.log")
TRIAL_ID_PATH = "/logs/artifacts/trial_id"


def _read_trial_id():
    with open(TRIAL_ID_PATH) as f:
        return f.read().strip()


def _expected_index_name():
    return f"harbor-managed-index-{_read_trial_id()}"


def _read_log():
    assert os.path.isfile(LOG_FILE), (
        f"Expected log file at {LOG_FILE} to exist after the task runs."
    )
    with open(LOG_FILE, encoding="utf-8", errors="replace") as f:
        return f.read()


def test_log_file_exists_and_non_empty():
    assert os.path.isfile(LOG_FILE), (
        f"Expected log file at {LOG_FILE} to exist after the task runs."
    )
    assert os.path.getsize(LOG_FILE) > 0, (
        f"Log file {LOG_FILE} must not be empty."
    )


def test_log_contains_index_name():
    content = _read_log()
    expected_name = _expected_index_name()
    expected_line = f"Index name: {expected_name}"
    assert expected_line in content, (
        f"Expected the log file to contain a line `{expected_line}`, "
        f"but it was not found. Log content:\n{content}"
    )


def test_log_contains_retrieved_nodes_count():
    content = _read_log()
    match = re.search(r"Retrieved nodes:\s*(\d+)", content)
    assert match is not None, (
        "Expected the log file to contain a line in the form "
        "`Retrieved nodes: <N>`, but no such line was found. "
        f"Log content:\n{content}"
    )
    count = int(match.group(1))
    assert count >= 1, (
        f"Expected `Retrieved nodes` count to be >= 1, but got {count}."
    )


def test_log_contains_node_text_lines_matching_count():
    content = _read_log()
    match = re.search(r"Retrieved nodes:\s*(\d+)", content)
    assert match is not None, (
        "Expected `Retrieved nodes: <N>` line in log to determine expected "
        "number of node text lines."
    )
    expected_count = int(match.group(1))
    node_text_lines = [
        line for line in content.splitlines() if line.startswith("Node text: ")
    ]
    assert len(node_text_lines) >= expected_count, (
        f"Expected at least {expected_count} `Node text: ` lines in the log, "
        f"but found {len(node_text_lines)}."
    )


def test_log_node_text_mentions_cat():
    content = _read_log()
    node_text_lines = [
        line for line in content.splitlines() if line.startswith("Node text: ")
    ]
    assert node_text_lines, (
        "Expected at least one `Node text: ` line in the log file."
    )
    combined = "\n".join(node_text_lines).lower()
    assert "cat" in combined, (
        "Expected at least one retrieved node's text to mention `cat` "
        "(case-insensitive), confirming the cats document was retrieved. "
        f"Got node text lines:\n{node_text_lines}"
    )


def test_managed_index_exists_in_llama_cloud():
    """Connect to LlamaCloud and verify the managed index actually exists."""
    api_key = os.environ.get("LLAMA_CLOUD_API_KEY")
    assert api_key, (
        "Verifier requires LLAMA_CLOUD_API_KEY to be set to query LlamaCloud."
    )
    try:
        from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
    except ImportError as exc:  # pragma: no cover
        pytest.fail(
            "Verifier requires `llama-index-indices-managed-llama-cloud` to be "
            f"installed. Import failed: {exc}"
        )

    expected_name = _expected_index_name()
    try:
        index = LlamaCloudIndex(
            name=expected_name,
            project_name="default",
            api_key=api_key,
        )
    except Exception as exc:
        pytest.fail(
            f"Could not connect to LlamaCloud managed index `{expected_name}` "
            f"in project `default`: {exc}"
        )

    # Sanity check: the index has an associated pipeline/id.
    pipeline = getattr(index, "pipeline", None)
    assert pipeline is not None, (
        f"Connected to index `{expected_name}` but no underlying pipeline was "
        "returned by LlamaCloud."
    )


def test_managed_index_retrieves_cat_content_from_llama_cloud():
    """Re-issue the retrieval against LlamaCloud to confirm ingestion worked."""
    api_key = os.environ.get("LLAMA_CLOUD_API_KEY")
    assert api_key, (
        "Verifier requires LLAMA_CLOUD_API_KEY to be set to query LlamaCloud."
    )
    from llama_index.indices.managed.llama_cloud import LlamaCloudIndex

    expected_name = _expected_index_name()
    index = LlamaCloudIndex(
        name=expected_name,
        project_name="default",
        api_key=api_key,
    )
    retriever = index.as_retriever(similarity_top_k=3)
    nodes = retriever.retrieve("What do cats like to eat?")
    assert nodes, (
        f"Expected LlamaCloud index `{expected_name}` to return at least one "
        "node for the query 'What do cats like to eat?', but got an empty "
        "result."
    )
    combined = " ".join(
        (getattr(n, "text", None) or n.get_content() or "") for n in nodes
    ).lower()
    assert "cat" in combined, (
        f"Expected retrieved content from index `{expected_name}` to mention "
        f"`cat`, but got: {combined[:500]!r}"
    )
