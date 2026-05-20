import os
import re
import subprocess

import pytest

PROJECT_DIR = "/home/user/update_task"
UPDATE_SCRIPT = os.path.join(PROJECT_DIR, "update_index.py")
OUTPUT_LOG = os.path.join(PROJECT_DIR, "output.log")
TRIAL_ID_PATH = "/logs/artifacts/trial_id"

AURORA_HEADER = "=== aurora retrieval ==="
CUISINE_HEADER = "=== cuisine retrieval ==="


def _read_trial_id() -> str:
    assert os.path.isfile(TRIAL_ID_PATH), (
        f"Trial id artifact missing at {TRIAL_ID_PATH}."
    )
    with open(TRIAL_ID_PATH, "r", encoding="utf-8") as fp:
        trial_id = fp.read().strip()
    assert trial_id, f"Trial id at {TRIAL_ID_PATH} is empty."
    return trial_id


def _section_text(log_text: str, header_line: str) -> str:
    """Return the text between `header_line` and either the next '=== ' header or end-of-file."""
    lines = log_text.splitlines()
    try:
        start_idx = lines.index(header_line)
    except ValueError:
        return ""
    out = []
    for line in lines[start_idx + 1:]:
        if line.startswith("=== ") and line.endswith(" ==="):
            break
        out.append(line)
    return "\n".join(out)


@pytest.fixture(scope="module")
def trial_id() -> str:
    return _read_trial_id()


@pytest.fixture(scope="module")
def expected_index_name(trial_id: str) -> str:
    return f"harbor-update-index-{trial_id}"


@pytest.fixture(scope="module")
def script_source() -> str:
    assert os.path.isfile(UPDATE_SCRIPT), (
        f"Expected the executor-created script at {UPDATE_SCRIPT}, but it is missing."
    )
    with open(UPDATE_SCRIPT, "r", encoding="utf-8") as fp:
        return fp.read()


@pytest.fixture(scope="module")
def script_output(expected_index_name: str, script_source: str):
    """Run update_index.py once and yield the produced log text."""
    # script_source touched so we fail fast if the script is missing.
    assert script_source

    if os.path.exists(OUTPUT_LOG):
        os.remove(OUTPUT_LOG)

    env = os.environ.copy()
    result = subprocess.run(
        ["python3", "update_index.py"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        env=env,
        timeout=1200,
    )
    assert result.returncode == 0, (
        "update_index.py did not exit with status 0.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )

    assert os.path.isfile(OUTPUT_LOG), (
        f"Expected output log at {OUTPUT_LOG} after running update_index.py, but it is missing."
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


def test_script_source_references_update_ref_doc(script_source: str):
    """The executor must wire LlamaCloud's upsert API: the script source must contain
    the literal substring `update_ref_doc`."""
    assert "update_ref_doc" in script_source, (
        f"Expected the literal substring 'update_ref_doc' in {UPDATE_SCRIPT}, but it was not found."
    )


def test_log_contains_index_name_line(script_output: str, expected_index_name: str):
    """The log must announce the exact LlamaCloud index name that was created."""
    expected_line = f"Index name: {expected_index_name}"
    assert expected_line in script_output, (
        f"Expected line '{expected_line}' in {OUTPUT_LOG}.\n"
        f"First 800 chars of log: {script_output[:800]!r}"
    )


def test_log_contains_updated_document_id_line(script_output: str):
    """The log must record which ref_doc_id was upserted via update_ref_doc."""
    expected_line = "Updated document id: atlantis-aurora"
    assert expected_line in script_output, (
        f"Expected line '{expected_line}' in {OUTPUT_LOG}.\n"
        f"First 800 chars of log: {script_output[:800]!r}"
    )


def test_log_contains_aurora_retrieval_section(script_output: str):
    """The log must contain a clearly delimited section for the aurora retrieval."""
    assert AURORA_HEADER in script_output.splitlines(), (
        f"Expected the exact header line '{AURORA_HEADER}' in {OUTPUT_LOG}.\n"
        f"First 1500 chars of log: {script_output[:1500]!r}"
    )


def test_log_contains_cuisine_retrieval_section(script_output: str):
    """The log must contain a clearly delimited section for the cuisine retrieval."""
    assert CUISINE_HEADER in script_output.splitlines(), (
        f"Expected the exact header line '{CUISINE_HEADER}' in {OUTPUT_LOG}.\n"
        f"First 1500 chars of log: {script_output[:1500]!r}"
    )


def test_aurora_section_reflects_updated_content(script_output: str):
    """In the aurora retrieval section, the new content from data/updates/atlantis-aurora.txt
    must be present, and the original content from data/initial/atlantis-aurora.txt must be absent."""
    section = _section_text(script_output, AURORA_HEADER)
    assert section.strip(), (
        f"Aurora retrieval section under '{AURORA_HEADER}' is empty in {OUTPUT_LOG}."
    )
    lowered = section.lower()
    assert "flying car" in lowered, (
        "Expected the corrected phrase 'flying car' (from data/updates/atlantis-aurora.txt) "
        f"in the aurora retrieval section, but it was not found. Section: {section[:1500]!r}"
    )
    assert "anti-gravity" in lowered, (
        "Expected the corrected phrase 'anti-gravity' (from data/updates/atlantis-aurora.txt) "
        f"in the aurora retrieval section, but it was not found. Section: {section[:1500]!r}"
    )
    assert "submarine" not in lowered, (
        "The original phrase 'submarine' (from data/initial/atlantis-aurora.txt) must no longer "
        f"appear in the aurora retrieval section after update_ref_doc. Section: {section[:1500]!r}"
    )
    assert "sonar-pulse" not in lowered, (
        "The original phrase 'sonar-pulse' (from data/initial/atlantis-aurora.txt) must no longer "
        f"appear in the aurora retrieval section after update_ref_doc. Section: {section[:1500]!r}"
    )


def test_cuisine_section_still_surfaces_untouched_document(script_output: str):
    """The cuisine retrieval section must surface a phrase from atlantis-cuisine.txt, proving
    the document that was NOT updated is still searchable."""
    section = _section_text(script_output, CUISINE_HEADER)
    assert section.strip(), (
        f"Cuisine retrieval section under '{CUISINE_HEADER}' is empty in {OUTPUT_LOG}."
    )
    lowered = section.lower()
    assert "grilled seaweed" in lowered, (
        "Expected the phrase 'grilled seaweed' (from data/initial/atlantis-cuisine.txt) "
        f"in the cuisine retrieval section, but it was not found. Section: {section[:1500]!r}"
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


def test_llama_cloud_pipeline_documents_after_update(
    expected_index_name: str, script_output: str
):
    """Use the LlamaCloud SDK to verify that after the update, both documents still
    exist in the pipeline (update_ref_doc is an upsert, not a deletion)."""
    # Touch the fixture so the script has already run before we query the API.
    assert script_output

    token = os.environ.get("LLAMA_CLOUD_API_KEY")
    assert token, "LLAMA_CLOUD_API_KEY is not set in the verifier environment."

    from llama_cloud.client import LlamaCloud

    client = LlamaCloud(token=token)
    pipelines = client.pipelines.search_pipelines(project_name="Default")
    matching = [p for p in pipelines if getattr(p, "name", None) == expected_index_name]
    assert matching, (
        f"Pipeline '{expected_index_name}' not found when checking pipeline documents."
    )
    pipeline_id = matching[0].id

    docs = client.pipelines.list_pipeline_documents(pipeline_id=pipeline_id)
    doc_ids = {getattr(d, "document_id", None) for d in docs}

    assert "atlantis-aurora" in doc_ids, (
        "Expected 'atlantis-aurora' to still be present in the managed pipeline after the "
        f"update (update_ref_doc upserts, not deletes). Current document ids: {doc_ids}"
    )
    assert "atlantis-cuisine" in doc_ids, (
        "Expected 'atlantis-cuisine' to still be present in the managed pipeline (it was "
        f"never modified). Current document ids: {doc_ids}"
    )
