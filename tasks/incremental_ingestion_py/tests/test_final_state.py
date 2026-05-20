import os
import re
import subprocess

import pytest

PROJECT_DIR = "/home/user/ingest_task"
INGEST_SCRIPT = os.path.join(PROJECT_DIR, "ingest.py")
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
    return f"harbor-incremental-index-{trial_id}"


@pytest.fixture(scope="module")
def script_output(expected_index_name: str):
    """Run ingest.py once and yield the produced log text."""
    assert os.path.isfile(INGEST_SCRIPT), (
        f"Expected the executor-created script at {INGEST_SCRIPT}, but it is missing."
    )

    if os.path.exists(OUTPUT_LOG):
        os.remove(OUTPUT_LOG)

    env = os.environ.copy()
    result = subprocess.run(
        ["python3", "ingest.py"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        env=env,
        timeout=1200,
    )
    assert result.returncode == 0, (
        "ingest.py did not exit with status 0.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )

    assert os.path.isfile(OUTPUT_LOG), (
        f"Expected output log at {OUTPUT_LOG} after running ingest.py, but it is missing."
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
        f"First 500 chars of log: {script_output[:500]!r}"
    )


def test_log_reports_inserted_documents_count(script_output: str):
    """The log must include an `Inserted documents: <N>` line with N >= 1."""
    match = re.search(r"(?m)^Inserted documents:\s*(\d+)\s*$", script_output)
    assert match is not None, (
        "Expected a line matching `Inserted documents: <N>` in the log.\n"
        f"First 500 chars of log: {script_output[:500]!r}"
    )
    count = int(match.group(1))
    assert count >= 1, (
        f"Expected at least 1 incrementally inserted document, but log reports {count}."
    )


def test_log_contains_retrieved_aurora_phrase(script_output: str):
    """The retriever output must surface the Atlantis Aurora fact from the inserted vehicles.txt."""
    lowered = script_output.lower()
    assert "atlantis aurora" in lowered, (
        "Expected the retrieved context to mention 'Atlantis Aurora' (from the incrementally inserted "
        f"vehicles.txt), but it was not found in {OUTPUT_LOG}. First 800 chars: {script_output[:800]!r}"
    )


def test_log_contains_retrieved_flying_car_phrase(script_output: str):
    """The retriever output must also surface the 'flying car' phrase from vehicles.txt."""
    lowered = script_output.lower()
    assert "flying car" in lowered, (
        "Expected the retrieved context to mention 'flying car' (from the incrementally inserted "
        f"vehicles.txt), but it was not found in {OUTPUT_LOG}. First 800 chars: {script_output[:800]!r}"
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
