import os
import re
import subprocess

import pytest

PROJECT_DIR = "/home/user/parse_pages_task"
SCRIPT_PATH = os.path.join(PROJECT_DIR, "parse_pages.py")
OUTPUT_MD = os.path.join(PROJECT_DIR, "output.md")
OUTPUT_LOG = os.path.join(PROJECT_DIR, "output.log")
TRIAL_ID_PATH = "/logs/artifacts/trial_id"

INCLUDED_MARKERS = (
    "Marker-Bravo-Page-One",
    "Marker-Delta-Page-Three",
)
EXCLUDED_MARKERS = (
    "Marker-Alpha-Page-Zero",
    "Marker-Charlie-Page-Two",
    "Marker-Echo-Page-Four",
)


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
    """Run parse_pages.py once and yield (markdown_text, log_text)."""
    # Pre-flight checks: script must exist and use the expected SDK / feature.
    source = _read_script_source()
    assert (
        "from llama_cloud_services import" in source
        or "from llama_parse import" in source
    ), (
        "Expected parse_pages.py to import LlamaParse from `llama_cloud_services` "
        f"or `llama_parse`, but neither import was found. First 500 chars of script: "
        f"{source[:500]!r}"
    )
    assert "target_pages" in source, (
        "Expected parse_pages.py to reference `target_pages` to configure the "
        f"LlamaParse page-selection feature. First 500 chars of script: {source[:500]!r}"
    )

    if os.path.exists(OUTPUT_MD):
        os.remove(OUTPUT_MD)
    if os.path.exists(OUTPUT_LOG):
        os.remove(OUTPUT_LOG)

    env = os.environ.copy()
    result = subprocess.run(
        ["python3", "parse_pages.py"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        env=env,
        timeout=600,
    )
    assert result.returncode == 0, (
        "parse_pages.py did not exit with status 0.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )

    assert os.path.isfile(OUTPUT_MD), (
        f"Expected markdown output at {OUTPUT_MD} after running parse_pages.py, but it is missing."
    )
    with open(OUTPUT_MD, "rb") as fp:
        md_bytes = fp.read()
    assert len(md_bytes) > 0, f"Markdown output {OUTPUT_MD} is empty."
    try:
        md_text = md_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        pytest.fail(f"Markdown output {OUTPUT_MD} is not valid UTF-8: {exc}")

    assert os.path.isfile(OUTPUT_LOG), (
        f"Expected log file at {OUTPUT_LOG} after running parse_pages.py, but it is missing."
    )
    with open(OUTPUT_LOG, "rb") as fp:
        log_bytes = fp.read()
    assert len(log_bytes) > 0, f"Log file {OUTPUT_LOG} is empty."
    try:
        log_text = log_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        pytest.fail(f"Log file {OUTPUT_LOG} is not valid UTF-8: {exc}")

    return md_text, log_text


def test_output_markdown_contains_requested_page_markers(script_outputs):
    md_text, _ = script_outputs
    for marker in INCLUDED_MARKERS:
        assert marker in md_text, (
            f"Expected the parsed markdown to contain '{marker}' (from one of the "
            f"two requested pages), but it was not found in {OUTPUT_MD}. "
            f"First 800 chars: {md_text[:800]!r}"
        )


def test_output_markdown_excludes_skipped_page_markers(script_outputs):
    md_text, _ = script_outputs
    for marker in EXCLUDED_MARKERS:
        assert marker not in md_text, (
            f"Did not expect the parsed markdown to contain '{marker}' because that "
            f"marker comes from a page that was supposed to be skipped via "
            f"target_pages=\"1,3\". Found it in {OUTPUT_MD}. "
            f"First 1200 chars: {md_text[:1200]!r}"
        )


def test_log_contains_trial_id_line(script_outputs, trial_id):
    _, log_text = script_outputs
    pattern = re.compile(rf"(?m)^Trial id:\s*{re.escape(trial_id)}\s*$")
    assert pattern.search(log_text) is not None, (
        f"Expected a line matching `Trial id: {trial_id}` in {OUTPUT_LOG}. "
        f"First 500 chars of log: {log_text[:500]!r}"
    )


def test_log_contains_target_pages_line(script_outputs):
    _, log_text = script_outputs
    pattern = re.compile(r"(?m)^Target pages:\s*1,3\s*$")
    assert pattern.search(log_text) is not None, (
        f"Expected a line matching `Target pages: 1,3` in {OUTPUT_LOG}. "
        f"First 500 chars of log: {log_text[:500]!r}"
    )


def test_log_contains_parsed_pages_count_two(script_outputs):
    _, log_text = script_outputs
    match = re.search(r"(?m)^Parsed pages count:\s*(\d+)\s*$", log_text)
    assert match is not None, (
        "Expected a line matching `Parsed pages count: <N>` in the log.\n"
        f"First 500 chars of log: {log_text[:500]!r}"
    )
    assert int(match.group(1)) == 2, (
        f"Expected `Parsed pages count: 2` (two pages requested via target_pages=1,3), "
        f"but log reports {match.group(1)}."
    )
