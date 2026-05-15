import os
import subprocess

import pytest

PROJECT_DIR = "/home/user/delete_task"
MANAGE_SCRIPT = os.path.join(PROJECT_DIR, "manage_index.py")
OUTPUT_LOG = os.path.join(PROJECT_DIR, "output.log")
TRIAL_ID_PATH = "/logs/artifacts/trial_id"


def _read_trial_id() -> str:
    assert os.path.isfile(TRIAL_ID_PATH), (
        f"Trial id artifact missing at {TRIAL_ID_PATH}."
    )
    with open(TRIAL_ID_PATH, "r", encoding="utf-8") as fp:
        trial_id = fp.read().strip()
    assert trial_id, f"Trial id at {TRIAL_ID_PATH} is empty."
    return trial_id


@pytest.fixture(scope="module")
def trial_id() -> str:
    return _read_trial_id()


@pytest.fixture(scope="module")
def expected_index_name(trial_id: str) -> str:
    return f"harbor-delete-index-{trial_id}"


@pytest.fixture(scope="module")
def script_output(expected_index_name: str):
    """Run manage_index.py once and yield the produced log text."""
    assert os.path.isfile(MANAGE_SCRIPT), (
        f"Expected the executor-created script at {MANAGE_SCRIPT}, but it is missing."
    )

    if os.path.exists(OUTPUT_LOG):
        os.remove(OUTPUT_LOG)

    env = os.environ.copy()
    result = subprocess.run(
        ["python3", "manage_index.py"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        env=env,
        timeout=1200,
    )
    assert result.returncode == 0, (
        "manage_index.py did not exit with status 0.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )

    assert os.path.isfile(OUTPUT_LOG), (
        f"Expected output log at {OUTPUT_LOG} after running manage_index.py, but it is missing."
    )

    with open(OUTPUT_LOG, "rb") as fp:
        raw = fp.read()
    assert len(raw) > 0, f"Output log {OUTPUT_LOG} is empty."

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        pytest.fail(f"Output log {OUTPUT_LOG} is not valid UTF-8: {exc}")

    yield text

    # Teardown: best-effort delete the created LlamaCloud pipeline so we
    # do not pollute the shared account between trials.
    try:
        from llama_cloud.client import LlamaCloud

        token = os.environ.get("LLAMA_CLOUD_API_KEY")
        if not token:
            return
        client = LlamaCloud(token=token)
        pipelines = client.pipelines.search_pipelines(project_name="Default")
        for p in pipelines:
            if getattr(p, "name", None) == expected_index_name:
                client.pipelines.delete_pipeline(pipeline_id=p.id)
    except Exception:
        # Cleanup is best-effort.
        pass


def test_log_contains_index_name_line(script_output: str, expected_index_name: str):
    """The log must announce the exact LlamaCloud index name that was created."""
    expected_line = f"Index name: {expected_index_name}"
    assert expected_line in script_output, (
        f"Expected line '{expected_line}' in {OUTPUT_LOG}.\n"
        f"First 800 chars of log: {script_output[:800]!r}"
    )


def test_log_contains_deleted_document_id_line(script_output: str):
    """The log must record which ref_doc_id was deleted."""
    expected_line = "Deleted document id: atlantis-secret"
    assert expected_line in script_output, (
        f"Expected line '{expected_line}' in {OUTPUT_LOG}.\n"
        f"First 800 chars of log: {script_output[:800]!r}"
    )


def test_log_retrieval_for_cuisine_still_contains_grilled_seaweed(script_output: str):
    """The retriever output for the national-dish query must still surface content
    from cuisine.txt, confirming the remaining (non-deleted) document is searchable."""
    lowered = script_output.lower()
    assert "grilled seaweed" in lowered, (
        "Expected the retrieved context to mention 'grilled seaweed' (from cuisine.txt), "
        f"but it was not found in {OUTPUT_LOG}. First 1500 chars: {script_output[:1500]!r}"
    )


def test_log_retrieval_for_lumina_sphere_is_absent(script_output: str):
    """After deletion, retrieval must NOT surface the deleted secret content. The phrase
    'Lumina Sphere' came exclusively from the deleted atlantis-secret document, so the
    retrieved context for the Lumina Sphere query must not contain it."""
    lowered = script_output.lower()
    assert "lumina sphere" not in lowered, (
        "The phrase 'Lumina Sphere' should not appear anywhere in the log because the "
        "document that referenced it (atlantis-secret) was deleted. Found it in "
        f"{OUTPUT_LOG}. First 1500 chars: {script_output[:1500]!r}"
    )


def test_llama_cloud_pipeline_exists(expected_index_name: str, script_output: str):
    """Use the LlamaCloud SDK to verify the managed index actually exists on the platform."""
    # Touch the fixture so the script has already run before we query the API.
    assert script_output

    token = os.environ.get("LLAMA_CLOUD_API_KEY")
    assert token, "LLAMA_CLOUD_API_KEY is not set in the verifier environment."

    from llama_cloud.client import LlamaCloud

    client = LlamaCloud(token=token)
    pipelines = client.pipelines.search_pipelines(project_name="Default")
    names = [getattr(p, "name", None) for p in pipelines]
    assert expected_index_name in names, (
        f"LlamaCloud Default project does not contain a pipeline named "
        f"'{expected_index_name}'. Found pipelines: {names}"
    )


def test_llama_cloud_pipeline_documents_reflect_deletion(
    expected_index_name: str, script_output: str
):
    """Use the LlamaCloud SDK to verify that the pipeline no longer holds the
    'atlantis-secret' document, while the other two documents remain."""
    # Touch the fixture so the script has already run before we query the API.
    assert script_output

    token = os.environ.get("LLAMA_CLOUD_API_KEY")
    assert token, "LLAMA_CLOUD_API_KEY is not set in the verifier environment."

    from llama_cloud.client import LlamaCloud

    client = LlamaCloud(token=token)
    pipelines = client.pipelines.search_pipelines(project_name="Default")
    matching = [p for p in pipelines if getattr(p, "name", None) == expected_index_name]
    assert matching, (
        f"Pipeline '{expected_index_name}' not found when checking remaining documents."
    )
    pipeline_id = matching[0].id

    docs = client.pipelines.list_pipeline_documents(pipeline_id=pipeline_id)
    doc_ids = {getattr(d, "document_id", None) for d in docs}

    assert "atlantis-secret" not in doc_ids, (
        "Expected 'atlantis-secret' to have been deleted from the managed pipeline, "
        f"but it is still present. Current document ids: {doc_ids}"
    )
    assert "atlantis-history" in doc_ids, (
        "Expected 'atlantis-history' to still be present in the managed pipeline, "
        f"but it is missing. Current document ids: {doc_ids}"
    )
    assert "atlantis-cuisine" in doc_ids, (
        "Expected 'atlantis-cuisine' to still be present in the managed pipeline, "
        f"but it is missing. Current document ids: {doc_ids}"
    )
