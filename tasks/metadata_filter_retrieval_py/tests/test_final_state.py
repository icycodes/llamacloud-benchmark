import os
import re
import subprocess

import pytest

PROJECT_DIR = "/home/user/metadata_filter_task"
SCRIPT_PATH = os.path.join(PROJECT_DIR, "filter_retrieve.py")
OUTPUT_LOG = os.path.join(PROJECT_DIR, "output.log")
TRIAL_ID_PATH = "/logs/artifacts/trial_id"

FINANCE_PHRASE = "globex industries"
SPORTS_PHRASE = "atlas kim"
GEOGRAPHY_PHRASE = "mount aurelius"

FINANCE_HEADER = "=== finance retrieval ==="
SPORTS_HEADER = "=== sports retrieval ==="


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
    return f"harbor-metadata-filter-index-{trial_id}"


@pytest.fixture(scope="module")
def script_source() -> str:
    assert os.path.isfile(SCRIPT_PATH), (
        f"Expected the executor-created script at {SCRIPT_PATH}, but it is missing."
    )
    with open(SCRIPT_PATH, "r", encoding="utf-8") as fp:
        return fp.read()


@pytest.fixture(scope="module")
def script_output(expected_index_name: str):
    """Run filter_retrieve.py once and yield the produced log text."""
    assert os.path.isfile(SCRIPT_PATH), (
        f"Expected the executor-created script at {SCRIPT_PATH}, but it is missing."
    )

    if os.path.exists(OUTPUT_LOG):
        os.remove(OUTPUT_LOG)

    env = os.environ.copy()
    result = subprocess.run(
        ["python3", "filter_retrieve.py"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        env=env,
        timeout=900,
    )
    assert result.returncode == 0, (
        "filter_retrieve.py did not exit with status 0.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )

    assert os.path.isfile(OUTPUT_LOG), (
        f"Expected output log at {OUTPUT_LOG} after running filter_retrieve.py, but it is missing."
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


def _section_after_header(text: str, header: str) -> str:
    """Return the chunk of `text` following the literal `header` line, up to the
    next `=== ... retrieval ===` section header or end of file."""
    idx = text.find(header)
    assert idx != -1, (
        f"Expected section header line {header!r} in the output log, but it was not found.\n"
        f"First 800 chars of log: {text[:800]!r}"
    )
    rest = text[idx + len(header):]
    # Stop at the next section header if one exists.
    next_header_match = re.search(r"^===\s+\S+\s+retrieval\s+===", rest, re.MULTILINE)
    if next_header_match:
        rest = rest[: next_header_match.start()]
    return rest


def test_script_references_metadata_filter_api(script_source: str):
    """The script must reference both `MetadataFilters` and `MetadataFilter`."""
    assert "MetadataFilters" in script_source, (
        f"Expected the substring 'MetadataFilters' in {SCRIPT_PATH}, "
        "but it was not found. The executor must use the LlamaIndex metadata-filter API."
    )
    assert "MetadataFilter" in script_source, (
        f"Expected the substring 'MetadataFilter' in {SCRIPT_PATH}, "
        "but it was not found. The executor must use the LlamaIndex metadata-filter API."
    )


def test_log_contains_index_name_line(script_output: str, expected_index_name: str):
    """The log must announce the exact LlamaCloud index name that was created."""
    expected_line = f"Index name: {expected_index_name}"
    assert expected_line in script_output, (
        f"Expected line '{expected_line}' in {OUTPUT_LOG}.\n"
        f"First 500 chars of log: {script_output[:500]!r}"
    )


def test_log_contains_document_count_three(script_output: str):
    """The log must record that exactly three documents were ingested."""
    match = re.search(r"^Document count:\s*(\d+)\s*$", script_output, re.MULTILINE)
    assert match is not None, (
        f"Expected a line matching '^Document count:\\s*(\\d+)\\s*$' in {OUTPUT_LOG}.\n"
        f"First 500 chars of log: {script_output[:500]!r}"
    )
    count = int(match.group(1))
    assert count == 3, (
        f"Expected Document count to be 3 (one per seeded file), got {count}."
    )


def test_finance_retrieval_only_returns_finance(script_output: str):
    """The finance-filtered retrieval must surface the finance phrase
    and must NOT surface the sports or geography phrases."""
    section = _section_after_header(script_output, FINANCE_HEADER).lower()

    assert FINANCE_PHRASE in section, (
        "Expected the case-insensitive substring 'Globex Industries' "
        "inside the finance retrieval section (originating from finance/finance.txt), "
        f"but it was not found. Section content: {section[:1000]!r}"
    )
    assert SPORTS_PHRASE not in section, (
        "Did not expect the case-insensitive substring 'Atlas Kim' "
        "inside the finance retrieval section. The metadata filter 'category == finance' "
        "should have excluded the sports document. "
        f"Section content: {section[:1000]!r}"
    )
    assert GEOGRAPHY_PHRASE not in section, (
        "Did not expect the case-insensitive substring 'Mount Aurelius' "
        "inside the finance retrieval section. The metadata filter 'category == finance' "
        "should have excluded the geography document. "
        f"Section content: {section[:1000]!r}"
    )


def test_sports_retrieval_only_returns_sports(script_output: str):
    """The sports-filtered retrieval must surface the sports phrase
    and must NOT surface the finance or geography phrases."""
    section = _section_after_header(script_output, SPORTS_HEADER).lower()

    assert SPORTS_PHRASE in section, (
        "Expected the case-insensitive substring 'Atlas Kim' "
        "inside the sports retrieval section (originating from sports/sports.txt), "
        f"but it was not found. Section content: {section[:1000]!r}"
    )
    assert FINANCE_PHRASE not in section, (
        "Did not expect the case-insensitive substring 'Globex Industries' "
        "inside the sports retrieval section. The metadata filter 'category == sports' "
        "should have excluded the finance document. "
        f"Section content: {section[:1000]!r}"
    )
    assert GEOGRAPHY_PHRASE not in section, (
        "Did not expect the case-insensitive substring 'Mount Aurelius' "
        "inside the sports retrieval section. The metadata filter 'category == sports' "
        "should have excluded the geography document. "
        f"Section content: {section[:1000]!r}"
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
