import json
import os
import re
import subprocess

import pytest

PROJECT_DIR = "/home/user/myproject"
SCRIPT_PATH = os.path.join(PROJECT_DIR, "parse_to_json.py")
SAMPLE_PDF = os.path.join(PROJECT_DIR, "manual.pdf")
OUTPUT_JSON = os.path.join(PROJECT_DIR, "parsed.json")
OUTPUT_LOG = os.path.join(PROJECT_DIR, "output.log")
TRIAL_ID_PATH = "/logs/artifacts/trial_id"

EXPECTED_HEADINGS = ("operations manual", "equipment list", "maintenance schedule")


def _read_trial_id() -> str:
    with open(TRIAL_ID_PATH, "r", encoding="utf-8") as f:
        return f.read().strip()


@pytest.fixture(scope="session", autouse=True)
def run_agent_script():
    """Clean previously generated outputs and execute the agent's script once."""
    assert os.path.isfile(SCRIPT_PATH), (
        f"Agent's script {SCRIPT_PATH} does not exist. The agent must create it."
    )
    assert os.path.isfile(SAMPLE_PDF), (
        f"Required input PDF {SAMPLE_PDF} is missing."
    )

    for path in (OUTPUT_JSON, OUTPUT_LOG):
        if os.path.isfile(path):
            os.remove(path)

    completed = subprocess.run(
        ["python3", SCRIPT_PATH],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=600,
    )
    yield completed


@pytest.fixture(scope="session")
def parsed_json(run_agent_script):
    assert os.path.isfile(OUTPUT_JSON), (
        f"Expected JSON output file at {OUTPUT_JSON} to be created by the script."
    )
    assert os.path.getsize(OUTPUT_JSON) > 0, (
        f"JSON output file {OUTPUT_JSON} exists but is empty."
    )
    with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def log_text(run_agent_script):
    assert os.path.isfile(OUTPUT_LOG), (
        f"Expected log file at {OUTPUT_LOG} to be created by the script."
    )
    assert os.path.getsize(OUTPUT_LOG) > 0, (
        f"Log file {OUTPUT_LOG} exists but is empty."
    )
    with open(OUTPUT_LOG, "r", encoding="utf-8") as f:
        return f.read()


def test_script_exit_code_is_zero(run_agent_script):
    """The agent's parse_to_json.py must run to completion with exit code 0."""
    completed = run_agent_script
    assert completed.returncode == 0, (
        f"parse_to_json.py exited with non-zero status {completed.returncode}.\n"
        f"STDOUT:\n{completed.stdout}\n"
        f"STDERR:\n{completed.stderr}"
    )


def test_parsed_json_is_dict_with_required_top_level_keys(parsed_json):
    """`parsed.json` must be a dict containing the required top-level keys."""
    assert isinstance(parsed_json, dict), (
        f"Expected the top-level value in parsed.json to be a JSON object (dict), "
        f"got {type(parsed_json).__name__}."
    )
    for key in ("trial_id", "source_file", "num_pages", "pages"):
        assert key in parsed_json, (
            f"Expected key `{key}` to be present at the top level of parsed.json. "
            f"Got keys: {sorted(parsed_json.keys())!r}."
        )


def test_parsed_json_trial_id_matches(parsed_json):
    """`parsed.json[\"trial_id\"]` must equal the value at /logs/artifacts/trial_id."""
    expected = _read_trial_id()
    actual = parsed_json.get("trial_id")
    assert isinstance(actual, str), (
        f"Expected `trial_id` to be a string in parsed.json, got {type(actual).__name__}."
    )
    assert actual == expected, (
        f"Expected `trial_id` in parsed.json to equal {expected!r}, got {actual!r}."
    )


def test_parsed_json_source_file_is_manual_pdf(parsed_json):
    """`parsed.json[\"source_file\"]` must equal `manual.pdf` (case-insensitive)."""
    value = parsed_json.get("source_file")
    assert isinstance(value, str), (
        f"Expected `source_file` to be a string in parsed.json, got {type(value).__name__}."
    )
    assert value.strip().lower() == "manual.pdf", (
        f"Expected `source_file` to equal 'manual.pdf' (case-insensitive), got {value!r}."
    )


def test_parsed_json_num_pages_is_consistent(parsed_json):
    """`num_pages` must be an integer >= 3 and equal to len(pages)."""
    num_pages = parsed_json.get("num_pages")
    pages = parsed_json.get("pages")
    assert isinstance(num_pages, int) and not isinstance(num_pages, bool), (
        f"Expected `num_pages` to be a plain integer, got {num_pages!r} "
        f"of type {type(num_pages).__name__}."
    )
    assert isinstance(pages, list), (
        f"Expected `pages` to be a list, got {type(pages).__name__}."
    )
    assert num_pages >= 3, (
        f"Expected `num_pages` >= 3 (the fixture has three pages), got {num_pages}."
    )
    assert num_pages == len(pages), (
        f"Expected `num_pages` ({num_pages}) to equal len(pages) ({len(pages)})."
    )


def test_pages_entries_have_required_fields(parsed_json):
    """Every page entry must have `page_number` (int), non-empty `text`, and non-empty `md`."""
    pages = parsed_json["pages"]
    assert len(pages) >= 3, (
        f"Expected at least 3 page entries in `pages`, got {len(pages)}."
    )
    for i, entry in enumerate(pages):
        assert isinstance(entry, dict), (
            f"Expected pages[{i}] to be a dict, got {type(entry).__name__}."
        )
        page_number = entry.get("page_number")
        assert isinstance(page_number, int) and not isinstance(page_number, bool), (
            f"Expected pages[{i}]['page_number'] to be an int, got {page_number!r}."
        )
        text = entry.get("text")
        md = entry.get("md")
        assert isinstance(text, str) and text.strip(), (
            f"Expected pages[{i}]['text'] to be a non-empty string."
        )
        assert isinstance(md, str) and md.strip(), (
            f"Expected pages[{i}]['md'] to be a non-empty string."
        )


def test_first_three_pages_are_numbered_in_order(parsed_json):
    """The first three page entries must have page_number values 1, 2, 3 in order."""
    pages = parsed_json["pages"]
    expected_first_three = [1, 2, 3]
    actual_first_three = [pages[i]["page_number"] for i in range(3)]
    assert actual_first_three == expected_first_three, (
        f"Expected the first three pages to have page_number values "
        f"{expected_first_three}, got {actual_first_three}."
    )


def test_aggregate_text_contains_expected_headings(parsed_json):
    """The concatenated `text` across pages must mention every expected heading."""
    pages = parsed_json["pages"]
    combined = " ".join(p.get("text", "") for p in pages).lower()
    for heading in EXPECTED_HEADINGS:
        assert heading in combined, (
            f"Expected the concatenated `text` across pages to mention {heading!r} "
            f"(case-insensitive), but it was not found."
        )


def test_aggregate_md_contains_expected_headings(parsed_json):
    """The concatenated `md` across pages must mention every expected heading."""
    pages = parsed_json["pages"]
    combined = " ".join(p.get("md", "") for p in pages).lower()
    for heading in EXPECTED_HEADINGS:
        assert heading in combined, (
            f"Expected the concatenated `md` across pages to mention {heading!r} "
            f"(case-insensitive), but it was not found."
        )


def test_output_log_trial_id_line(log_text):
    """`output.log` must contain a `trial_id: <trial_id>` line."""
    expected = _read_trial_id()
    pattern = re.compile(
        r"^\s*trial_id\s*:\s*" + re.escape(expected) + r"\s*$",
        re.MULTILINE,
    )
    assert pattern.search(log_text), (
        f"Expected output.log to contain a line `trial_id: {expected}`, "
        f"matching the value at {TRIAL_ID_PATH}, but no such line was found.\n"
        f"Log content:\n{log_text!r}"
    )


def test_output_log_source_file_line(log_text):
    """`output.log` must contain a `source_file: manual.pdf` line (case-insensitive on value)."""
    pattern = re.compile(
        r"^\s*source_file\s*:\s*manual\.pdf\s*$",
        re.MULTILINE | re.IGNORECASE,
    )
    assert pattern.search(log_text), (
        f"Expected output.log to contain a line `source_file: manual.pdf` "
        f"(case-insensitive on the value), but no such line was found.\n"
        f"Log content:\n{log_text!r}"
    )


def test_output_log_num_pages_line_matches_parsed_json(log_text, parsed_json):
    """`output.log` must contain a `num_pages: <N>` line where N matches parsed.json."""
    match = re.search(
        r"^\s*num_pages\s*:\s*(\d+)\s*$",
        log_text,
        re.MULTILINE,
    )
    assert match, (
        f"Expected output.log to contain a line matching `num_pages: <N>` "
        f"where N is a non-negative integer, but no such line was found.\n"
        f"Log content:\n{log_text!r}"
    )
    log_num = int(match.group(1))
    expected_num = parsed_json.get("num_pages")
    assert log_num >= 3, (
        f"Expected log `num_pages` to be at least 3, got {log_num}."
    )
    assert log_num == expected_num, (
        f"Expected log `num_pages` ({log_num}) to equal parsed.json `num_pages` "
        f"({expected_num})."
    )
