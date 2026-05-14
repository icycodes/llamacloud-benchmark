import json
import os
import re
import subprocess
import pytest

PROJECT_DIR = "/home/user/myproject"
EXTRACT_SCRIPT = os.path.join(PROJECT_DIR, "extract_tables.py")
TABLES_DIR = os.path.join(PROJECT_DIR, "tables")
SUMMARY_JSON = os.path.join(PROJECT_DIR, "tables_summary.json")
SAMPLE_PDF = os.path.join(PROJECT_DIR, "quarterly_report.pdf")

FILENAME_RE = re.compile(r"^table_p\d{3}_\d+\.csv$")
EXPECTED_HEADER_TOKENS = (
    "Revenue", "Quarter", "Profit",
    "Department", "Headcount", "Open Roles",
)


def _maybe_run_extract_script():
    """If the agent did not leave the output files in place, re-run the script
    once with the verifier's LLAMA_CLOUD_API_KEY so the artifacts are present
    for the assertions below."""
    if os.path.isfile(SUMMARY_JSON) and os.path.isdir(TABLES_DIR):
        csvs = [f for f in os.listdir(TABLES_DIR) if f.endswith(".csv")]
        if csvs:
            return
    if not os.path.isfile(EXTRACT_SCRIPT):
        return
    subprocess.run(
        ["python3", EXTRACT_SCRIPT],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=300,
    )


def test_extract_script_exists():
    assert os.path.isfile(EXTRACT_SCRIPT), \
        f"Expected the agent to create {EXTRACT_SCRIPT}, but it does not exist."


def test_extract_script_uses_llamaparse_sdk():
    with open(EXTRACT_SCRIPT, "r", encoding="utf-8", errors="replace") as f:
        contents = f.read()
    uses_services = "llama_cloud_services" in contents or "llama-cloud-services" in contents
    uses_client = "llama_cloud" in contents or "LlamaCloud" in contents or "LlamaParse" in contents
    assert uses_services or uses_client, (
        "extract_tables.py must import or reference a LlamaParse client from either "
        "'llama_cloud_services' or 'llama_cloud'."
    )


def test_sample_pdf_unchanged():
    assert os.path.isfile(SAMPLE_PDF), \
        f"Source PDF {SAMPLE_PDF} must remain in place."
    with open(SAMPLE_PDF, "rb") as f:
        header = f.read(5)
    assert header.startswith(b"%PDF-"), \
        f"Source PDF {SAMPLE_PDF} is no longer a valid PDF."


def test_tables_dir_exists_and_has_csv():
    _maybe_run_extract_script()
    assert os.path.isdir(TABLES_DIR), \
        f"Expected the agent to create directory {TABLES_DIR}."
    csv_files = [f for f in os.listdir(TABLES_DIR) if f.endswith(".csv")]
    assert len(csv_files) >= 1, \
        f"Expected at least one .csv file inside {TABLES_DIR}, got: {csv_files}"


def test_csv_filenames_follow_pattern():
    _maybe_run_extract_script()
    csv_files = [f for f in os.listdir(TABLES_DIR) if f.endswith(".csv")]
    bad = [f for f in csv_files if not FILENAME_RE.match(f)]
    assert not bad, (
        f"All CSV filenames in {TABLES_DIR} must match the pattern "
        f"'table_p{{NNN}}_{{i}}.csv', but these did not: {bad}"
    )


def test_summary_json_exists_and_non_empty():
    _maybe_run_extract_script()
    assert os.path.isfile(SUMMARY_JSON), \
        f"Expected summary JSON at {SUMMARY_JSON}, but it does not exist."
    assert os.path.getsize(SUMMARY_JSON) > 0, \
        f"Summary JSON {SUMMARY_JSON} is empty."


def _load_summary():
    with open(SUMMARY_JSON, "r", encoding="utf-8", errors="replace") as f:
        return json.load(f)


def test_summary_json_has_required_keys():
    _maybe_run_extract_script()
    data = _load_summary()
    for key in ("source", "table_count", "tables"):
        assert key in data, \
            f"Summary JSON is missing required top-level key '{key}'. Got keys: {list(data.keys())}"


def test_summary_source_field():
    _maybe_run_extract_script()
    data = _load_summary()
    assert data["source"] == "quarterly_report.pdf", \
        f"Expected summary 'source' to be 'quarterly_report.pdf', got: {data['source']!r}"


def test_summary_tables_is_non_empty_list():
    _maybe_run_extract_script()
    data = _load_summary()
    tables = data["tables"]
    assert isinstance(tables, list), \
        f"Summary 'tables' must be a JSON list, got: {type(tables).__name__}"
    assert len(tables) >= 1, \
        f"Summary 'tables' must contain at least one entry, got: {tables}"


def test_summary_table_count_matches_list():
    _maybe_run_extract_script()
    data = _load_summary()
    assert data["table_count"] == len(data["tables"]), (
        f"'table_count' ({data['table_count']}) must equal len(tables) "
        f"({len(data['tables'])})."
    )


def test_summary_entries_well_formed():
    _maybe_run_extract_script()
    data = _load_summary()
    for entry in data["tables"]:
        assert isinstance(entry, dict), \
            f"Each entry in 'tables' must be a dict, got: {entry!r}"
        for key, expected_type in (("page", int), ("file", str), ("rows", int), ("cols", int)):
            assert key in entry, \
                f"Each entry must contain key '{key}', missing in: {entry}"
            assert isinstance(entry[key], expected_type), (
                f"Entry key '{key}' must be {expected_type.__name__}, "
                f"got {type(entry[key]).__name__} in entry: {entry}"
            )
        assert entry["page"] >= 1, \
            f"Entry 'page' must be >= 1 (1-indexed), got: {entry['page']}"
        assert entry["rows"] >= 1, \
            f"Entry 'rows' must be >= 1, got: {entry['rows']}"
        assert entry["cols"] >= 1, \
            f"Entry 'cols' must be >= 1, got: {entry['cols']}"
        assert FILENAME_RE.match(entry["file"]), (
            f"Entry 'file' must match 'table_p{{NNN}}_{{i}}.csv', "
            f"got: {entry['file']!r}"
        )


def test_summary_files_exist_on_disk():
    _maybe_run_extract_script()
    data = _load_summary()
    for entry in data["tables"]:
        csv_path = os.path.join(TABLES_DIR, entry["file"])
        assert os.path.isfile(csv_path), \
            f"Summary references {entry['file']}, but {csv_path} does not exist."


def test_summary_sorted_by_page_then_file():
    _maybe_run_extract_script()
    data = _load_summary()
    keys = [(e["page"], e["file"]) for e in data["tables"]]
    assert keys == sorted(keys), (
        f"Summary 'tables' must be ordered by (page ASC, file ASC), got order: {keys}"
    )


def test_csv_contents_include_expected_header_token():
    _maybe_run_extract_script()
    csv_files = [f for f in os.listdir(TABLES_DIR) if f.endswith(".csv")]
    combined = ""
    for f in csv_files:
        with open(os.path.join(TABLES_DIR, f), "r", encoding="utf-8", errors="replace") as fh:
            combined += fh.read()
    matched = [tok for tok in EXPECTED_HEADER_TOKENS if tok in combined]
    assert matched, (
        f"Expected at least one of {list(EXPECTED_HEADER_TOKENS)} to appear in "
        f"the extracted CSVs, but found none. CSV files: {csv_files}"
    )
