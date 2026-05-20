import json
import os
import re
import subprocess

import pytest

PROJECT_DIR = "/home/user/parse_json_task"
SCRIPT_PATH = os.path.join(PROJECT_DIR, "parse_to_json.py")
OUTPUT_JSON = os.path.join(PROJECT_DIR, "output.json")
OUTPUT_LOG = os.path.join(PROJECT_DIR, "output.log")
TRIAL_ID_PATH = "/logs/artifacts/trial_id"

EXPECTED_PAGE_DATA = {
    1: ("JSON-Mode-Page-One", "500,000"),
    2: ("JSON-Mode-Page-Two", "750,000"),
    3: ("JSON-Mode-Page-Three", "1,000,000"),
}


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


def _read_script_source() -> str:
    assert os.path.isfile(SCRIPT_PATH), (
        f"Expected the executor-created script at {SCRIPT_PATH}, but it is missing."
    )
    with open(SCRIPT_PATH, "r", encoding="utf-8") as fp:
        return fp.read()


@pytest.fixture(scope="module")
def script_outputs():
    """Run parse_to_json.py once and yield (parsed_json, log_text)."""
    source = _read_script_source()
    assert (
        "from llama_cloud_services import" in source
        or "from llama_parse import" in source
    ), (
        "Expected parse_to_json.py to import LlamaParse from `llama_cloud_services` "
        f"or `llama_parse`, but neither import was found. First 500 chars of script: "
        f"{source[:500]!r}"
    )
    assert "result_type" in source and '"json"' in source, (
        "Expected parse_to_json.py to configure LlamaParse with `result_type=\"json\"` "
        f"to use the JSON output mode. First 800 chars of script: {source[:800]!r}"
    )
    assert "get_json_result" in source, (
        "Expected parse_to_json.py to call `get_json_result` so that LlamaParse's "
        f"JSON-mode entry point is actually used. First 800 chars of script: {source[:800]!r}"
    )

    if os.path.exists(OUTPUT_JSON):
        os.remove(OUTPUT_JSON)
    if os.path.exists(OUTPUT_LOG):
        os.remove(OUTPUT_LOG)

    env = os.environ.copy()
    result = subprocess.run(
        ["python3", "parse_to_json.py"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        env=env,
        timeout=600,
    )
    assert result.returncode == 0, (
        "parse_to_json.py did not exit with status 0.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )

    assert os.path.isfile(OUTPUT_JSON), (
        f"Expected JSON manifest at {OUTPUT_JSON} after running parse_to_json.py, but it is missing."
    )
    with open(OUTPUT_JSON, "rb") as fp:
        raw = fp.read()
    assert len(raw) > 0, f"JSON manifest {OUTPUT_JSON} is empty."
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        pytest.fail(f"JSON manifest {OUTPUT_JSON} is not valid UTF-8: {exc}")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        pytest.fail(f"JSON manifest {OUTPUT_JSON} does not parse as JSON: {exc}")

    assert os.path.isfile(OUTPUT_LOG), (
        f"Expected log file at {OUTPUT_LOG} after running parse_to_json.py, but it is missing."
    )
    with open(OUTPUT_LOG, "rb") as fp:
        log_bytes = fp.read()
    assert len(log_bytes) > 0, f"Log file {OUTPUT_LOG} is empty."
    try:
        log_text = log_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        pytest.fail(f"Log file {OUTPUT_LOG} is not valid UTF-8: {exc}")

    return parsed, log_text


def test_manifest_has_required_top_level_keys(script_outputs):
    parsed, _ = script_outputs
    assert isinstance(parsed, dict), (
        f"Expected the JSON manifest top-level value to be an object, "
        f"got {type(parsed).__name__}."
    )
    for key in ("trial_id", "job_id", "page_count", "pages"):
        assert key in parsed, (
            f"Expected top-level key '{key}' in {OUTPUT_JSON}, but it is missing. "
            f"Keys present: {sorted(parsed.keys())}"
        )


def test_manifest_trial_id_matches_artifact(script_outputs, trial_id):
    parsed, _ = script_outputs
    assert parsed.get("trial_id") == trial_id, (
        f"Expected `trial_id` in {OUTPUT_JSON} to equal '{trial_id}' (the value "
        f"read from {TRIAL_ID_PATH}), but got {parsed.get('trial_id')!r}."
    )


def test_manifest_page_count_is_three(script_outputs):
    parsed, _ = script_outputs
    assert parsed.get("page_count") == 3, (
        f"Expected `page_count` to equal the integer 3 in {OUTPUT_JSON}, "
        f"but got {parsed.get('page_count')!r}."
    )


def test_manifest_pages_array_has_three_sorted_entries(script_outputs):
    parsed, _ = script_outputs
    pages = parsed.get("pages")
    assert isinstance(pages, list), (
        f"Expected `pages` in {OUTPUT_JSON} to be a JSON array, got {type(pages).__name__}."
    )
    assert len(pages) == 3, (
        f"Expected `pages` to be a list of length 3 in {OUTPUT_JSON}, got length {len(pages)}."
    )
    page_numbers = [entry.get("page") for entry in pages]
    assert page_numbers == [1, 2, 3], (
        f"Expected `pages` to be sorted ascending with page numbers [1, 2, 3] in {OUTPUT_JSON}, "
        f"got {page_numbers}."
    )
    for index, entry in enumerate(pages):
        assert isinstance(entry, dict), (
            f"Expected each `pages` entry to be a JSON object, "
            f"but entry at index {index} is {type(entry).__name__}."
        )
        for key in ("page", "text", "markdown"):
            assert key in entry, (
                f"Expected `pages[{index}]` in {OUTPUT_JSON} to contain key '{key}', "
                f"but the entry only has keys {sorted(entry.keys())}."
            )


@pytest.mark.parametrize("page_number", [1, 2, 3])
def test_each_page_text_contains_marker_and_amount(script_outputs, page_number):
    parsed, _ = script_outputs
    pages = parsed.get("pages", [])
    entry = next((p for p in pages if p.get("page") == page_number), None)
    assert entry is not None, (
        f"Expected `pages` in {OUTPUT_JSON} to contain an entry for page {page_number}."
    )
    marker, amount = EXPECTED_PAGE_DATA[page_number]
    text_field = entry.get("text", "")
    assert isinstance(text_field, str), (
        f"Expected `pages[{page_number - 1}].text` to be a string in {OUTPUT_JSON}, "
        f"got {type(text_field).__name__}."
    )
    assert marker in text_field, (
        f"Expected the `text` field of page {page_number} to contain marker '{marker}', "
        f"but it was missing. First 800 chars of text: {text_field[:800]!r}"
    )
    assert amount in text_field, (
        f"Expected the `text` field of page {page_number} to contain the revenue amount "
        f"'{amount}', but it was missing. First 800 chars of text: {text_field[:800]!r}"
    )


def test_log_contains_trial_id_line(script_outputs, trial_id):
    _, log_text = script_outputs
    pattern = re.compile(rf"(?m)^Trial id:\s*{re.escape(trial_id)}\s*$")
    assert pattern.search(log_text) is not None, (
        f"Expected a line matching `Trial id: {trial_id}` in {OUTPUT_LOG}. "
        f"First 500 chars of log: {log_text[:500]!r}"
    )


def test_log_contains_page_count_line(script_outputs):
    _, log_text = script_outputs
    assert re.search(r"(?m)^Page count:\s*3\s*$", log_text) is not None, (
        f"Expected a line matching `Page count: 3` in {OUTPUT_LOG}. "
        f"First 500 chars of log: {log_text[:500]!r}"
    )


def test_log_job_id_matches_manifest(script_outputs):
    parsed, log_text = script_outputs
    match = re.search(r"(?m)^Job id:\s*(\S+)\s*$", log_text)
    assert match is not None, (
        f"Expected a line matching `Job id: <job_id>` in {OUTPUT_LOG}. "
        f"First 500 chars of log: {log_text[:500]!r}"
    )
    log_job_id = match.group(1)
    manifest_job_id = parsed.get("job_id")
    assert manifest_job_id, (
        f"Expected non-empty `job_id` in {OUTPUT_JSON}, got {manifest_job_id!r}."
    )
    assert log_job_id == manifest_job_id, (
        f"Expected `Job id` in {OUTPUT_LOG} (={log_job_id!r}) to match the "
        f"`job_id` stored at the top level of {OUTPUT_JSON} (={manifest_job_id!r})."
    )
