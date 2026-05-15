import json
import os
import re
import subprocess

import pytest

PROJECT_DIR = "/home/user/myproject"
SCRIPT_PATH = os.path.join(PROJECT_DIR, "extract_tables.py")
SAMPLE_PDF = os.path.join(PROJECT_DIR, "report.pdf")
OUTPUT_JSON = os.path.join(PROJECT_DIR, "tables.json")
OUTPUT_LOG = os.path.join(PROJECT_DIR, "output.log")
TRIAL_ID_PATH = "/logs/artifacts/trial_id"

HEADER_SEPARATOR_RE = re.compile(r"\|\s*[-:][- :]*\s*\|")


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
        f"Required sample PDF {SAMPLE_PDF} is missing."
    )

    # Cleanup any pre-existing artifacts so the test verifies fresh outputs.
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


def _load_tables_json():
    with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def test_script_exit_code_is_zero(run_agent_script):
    """The agent's extract_tables.py must run to completion with exit code 0."""
    completed = run_agent_script
    assert completed.returncode == 0, (
        f"extract_tables.py exited with non-zero status {completed.returncode}.\n"
        f"STDOUT:\n{completed.stdout}\n"
        f"STDERR:\n{completed.stderr}"
    )


def test_output_json_file_exists():
    """The structured tables JSON output file must exist and be non-empty."""
    assert os.path.isfile(OUTPUT_JSON), (
        f"Expected JSON output file at {OUTPUT_JSON} to be created by the script."
    )
    assert os.path.getsize(OUTPUT_JSON) > 0, (
        f"JSON output file {OUTPUT_JSON} exists but is empty."
    )


def test_output_json_top_level_shape():
    """tables.json must be valid JSON with the required top-level keys."""
    try:
        data = _load_tables_json()
    except json.JSONDecodeError as exc:
        pytest.fail(f"{OUTPUT_JSON} is not valid JSON: {exc}")
    assert isinstance(data, dict), (
        f"Expected {OUTPUT_JSON} top level to be a JSON object, got "
        f"{type(data).__name__}."
    )
    for key in ("trial_id", "num_pages", "num_tables", "tables"):
        assert key in data, (
            f"Expected key `{key}` to be present in {OUTPUT_JSON}. "
            f"Top-level keys present: {sorted(data.keys())!r}"
        )


def test_output_json_trial_id_matches():
    """The `trial_id` in tables.json must match the harness `trial_id` value."""
    data = _load_tables_json()
    expected = _read_trial_id()
    assert data.get("trial_id") == expected, (
        f"Expected tables.json `trial_id` to equal `{expected}` "
        f"(from {TRIAL_ID_PATH}), got `{data.get('trial_id')!r}`."
    )


def test_output_json_num_pages_is_positive_integer():
    """`num_pages` must be a non-negative integer >= 1."""
    data = _load_tables_json()
    num_pages = data.get("num_pages")
    assert isinstance(num_pages, int) and not isinstance(num_pages, bool), (
        f"Expected `num_pages` in {OUTPUT_JSON} to be an integer, got "
        f"{type(num_pages).__name__}: {num_pages!r}."
    )
    assert num_pages >= 1, (
        f"Expected `num_pages` in {OUTPUT_JSON} to be >= 1, got {num_pages}."
    )


def test_output_json_num_tables_consistent_and_at_least_two():
    """`num_tables` must be >= 2 and match the length of `tables`."""
    data = _load_tables_json()
    num_tables = data.get("num_tables")
    tables = data.get("tables")
    assert isinstance(num_tables, int) and not isinstance(num_tables, bool), (
        f"Expected `num_tables` in {OUTPUT_JSON} to be an integer, got "
        f"{type(num_tables).__name__}: {num_tables!r}."
    )
    assert isinstance(tables, list), (
        f"Expected `tables` in {OUTPUT_JSON} to be a list, got "
        f"{type(tables).__name__}."
    )
    assert num_tables >= 2, (
        f"Expected at least 2 tables to be extracted from the report, got "
        f"num_tables={num_tables}. The report contains a `Revenue by Product` "
        f"table on page 1 and a `Regional Sales` table on page 2."
    )
    assert num_tables == len(tables), (
        f"Expected `num_tables` ({num_tables}) to equal `len(tables)` "
        f"({len(tables)}) in {OUTPUT_JSON}."
    )


def test_output_json_table_entries_have_expected_structure():
    """Every entry in `tables` must have integer `page` >= 1 and a Markdown table string."""
    data = _load_tables_json()
    for idx, entry in enumerate(data["tables"]):
        assert isinstance(entry, dict), (
            f"Expected `tables[{idx}]` to be a dict, got {type(entry).__name__}."
        )
        page = entry.get("page")
        assert isinstance(page, int) and not isinstance(page, bool), (
            f"Expected `tables[{idx}].page` to be an integer, got "
            f"{type(page).__name__}: {page!r}."
        )
        assert page >= 1, (
            f"Expected `tables[{idx}].page` >= 1, got {page}."
        )
        markdown = entry.get("markdown")
        assert isinstance(markdown, str) and markdown.strip(), (
            f"Expected `tables[{idx}].markdown` to be a non-empty string."
        )
        lines = [ln for ln in markdown.splitlines() if ln.strip()]
        assert any(ln.lstrip().startswith("|") for ln in lines), (
            f"Expected `tables[{idx}].markdown` to contain at least one line "
            f"starting with `|`, but none was found.\nMarkdown:\n{markdown!r}"
        )
        assert HEADER_SEPARATOR_RE.search(markdown), (
            f"Expected `tables[{idx}].markdown` to contain a Markdown header-"
            f"separator row matching the regex `\\|\\s*[-: ]+\\s*\\|` (e.g. "
            f"`|---|---|`), but none was found.\nMarkdown:\n{markdown!r}"
        )


def test_output_json_tables_cover_revenue_by_product_content():
    """The combined Markdown of all tables must include 'Widget A' and 'Service Plan'."""
    data = _load_tables_json()
    combined = "\n".join(entry.get("markdown", "") for entry in data["tables"]).lower()
    assert "widget a" in combined, (
        "Expected the extracted tables to include the row label `Widget A` "
        "from the Revenue by Product table, but it was not found in any of "
        "the markdown strings."
    )
    assert "service plan" in combined, (
        "Expected the extracted tables to include the row label `Service Plan` "
        "from the Revenue by Product table, but it was not found in any of "
        "the markdown strings."
    )


def test_output_json_tables_cover_regional_sales_content():
    """The combined Markdown of all tables must include 'North America' and 'Asia Pacific'."""
    data = _load_tables_json()
    combined = "\n".join(entry.get("markdown", "") for entry in data["tables"]).lower()
    assert "north america" in combined, (
        "Expected the extracted tables to include the row label `North America` "
        "from the Regional Sales table, but it was not found in any of "
        "the markdown strings."
    )
    assert "asia pacific" in combined, (
        "Expected the extracted tables to include the row label `Asia Pacific` "
        "from the Regional Sales table, but it was not found in any of "
        "the markdown strings."
    )


def test_output_log_file_exists():
    """The log file written by the script must exist and be non-empty."""
    assert os.path.isfile(OUTPUT_LOG), (
        f"Expected log file at {OUTPUT_LOG} to be created by the script."
    )
    assert os.path.getsize(OUTPUT_LOG) > 0, (
        f"Log file {OUTPUT_LOG} exists but is empty."
    )


def test_output_log_contains_trial_id_line():
    """The log file must contain `trial_id: <value>` matching the harness value."""
    trial_id = _read_trial_id()
    with open(OUTPUT_LOG, "r", encoding="utf-8") as f:
        log_content = f.read()
    pattern = re.compile(
        r"^\s*trial_id\s*:\s*" + re.escape(trial_id) + r"\s*$",
        re.MULTILINE,
    )
    assert pattern.search(log_content), (
        f"Expected {OUTPUT_LOG} to contain a line `trial_id: {trial_id}` "
        f"matching the value at {TRIAL_ID_PATH}, but no such line was found.\n"
        f"Log content:\n{log_content!r}"
    )


def test_output_log_contains_num_pages_line():
    """The log file must contain a `num_pages: <N>` line with N >= 1."""
    with open(OUTPUT_LOG, "r", encoding="utf-8") as f:
        log_content = f.read()
    match = re.search(r"^\s*num_pages\s*:\s*(\d+)\s*$", log_content, re.MULTILINE)
    assert match, (
        f"Expected {OUTPUT_LOG} to contain a line matching `num_pages: <N>` "
        f"with N a non-negative integer, but no such line was found.\n"
        f"Log content:\n{log_content!r}"
    )
    n = int(match.group(1))
    assert n >= 1, f"Expected num_pages to be at least 1, got {n}."


def test_output_log_contains_num_tables_line():
    """The log file must contain a `num_tables: <M>` line with M >= 2."""
    with open(OUTPUT_LOG, "r", encoding="utf-8") as f:
        log_content = f.read()
    match = re.search(r"^\s*num_tables\s*:\s*(\d+)\s*$", log_content, re.MULTILINE)
    assert match, (
        f"Expected {OUTPUT_LOG} to contain a line matching `num_tables: <M>` "
        f"with M a non-negative integer, but no such line was found.\n"
        f"Log content:\n{log_content!r}"
    )
    m = int(match.group(1))
    assert m >= 2, (
        f"Expected num_tables to be at least 2 (the report contains two "
        f"tables), got {m}."
    )
