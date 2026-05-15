import csv
import glob
import os
import re
import shutil
import subprocess

import pytest

PROJECT_DIR = "/home/user/tables_task"
SCRIPT_PATH = os.path.join(PROJECT_DIR, "extract_tables.py")
TABLES_DIR = os.path.join(PROJECT_DIR, "tables")
LOG_PATH = os.path.join(PROJECT_DIR, "output.log")
TRIAL_ID_PATH = "/logs/artifacts/trial_id"


def _strip_cell(value):
    """Normalize a CSV cell for comparison: strip whitespace, $, commas."""
    if value is None:
        return ""
    return value.replace("$", "").replace(",", "").strip()


def _parse_int_cell(value):
    cleaned = _strip_cell(value)
    return int(cleaned)


@pytest.fixture(scope="module")
def trial_id():
    """Read the active trial id, used for log assertions."""
    with open(TRIAL_ID_PATH, "r", encoding="utf-8") as handle:
        value = handle.read().strip()
    assert value, f"Expected non-empty trial id in {TRIAL_ID_PATH}."
    return value


@pytest.fixture(scope="module")
def run_extract_tables():
    """Run the executor's script and yield the resulting CompletedProcess."""
    # Cleanup any pre-existing artifacts so we verify newly produced output.
    if os.path.isdir(TABLES_DIR):
        shutil.rmtree(TABLES_DIR)
    if os.path.isfile(LOG_PATH):
        os.remove(LOG_PATH)

    assert os.path.isfile(SCRIPT_PATH), (
        f"Expected the executor to create the script {SCRIPT_PATH}."
    )

    result = subprocess.run(
        ["python3", SCRIPT_PATH],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=300,
    )
    return result


def test_script_uses_llama_cloud_sdk():
    """The script must import the official llama_cloud SDK (v2 API)."""
    with open(SCRIPT_PATH, "r", encoding="utf-8") as handle:
        source = handle.read()
    assert ("from llama_cloud" in source) or ("import llama_cloud" in source), (
        "extract_tables.py must import from the official llama_cloud SDK "
        "(e.g. 'from llama_cloud import LlamaCloud')."
    )


def test_script_configures_items_expand():
    """The script must request the items tree via expand=['items']."""
    with open(SCRIPT_PATH, "r", encoding="utf-8") as handle:
        source = handle.read()
    assert "expand" in source, (
        "extract_tables.py must contain the literal substring 'expand' (LlamaParse v2 expand parameter)."
    )
    assert "items" in source, (
        "extract_tables.py must contain the literal substring 'items' (LlamaParse v2 items tree expand value)."
    )


def test_script_runs_successfully(run_extract_tables):
    """The executor's script must exit with status code 0."""
    result = run_extract_tables
    assert result.returncode == 0, (
        "extract_tables.py exited with non-zero status.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )


def test_csv_directory_contains_two_tables(run_extract_tables):
    """The script must write at least two CSV files following the table_NNN.csv convention."""
    assert os.path.isdir(TABLES_DIR), (
        f"Expected the script to create the CSV directory {TABLES_DIR}."
    )
    csv_files = sorted(
        path
        for path in glob.glob(os.path.join(TABLES_DIR, "*.csv"))
        if re.match(r"^table_\d{3}\.csv$", os.path.basename(path))
    )
    assert len(csv_files) >= 2, (
        f"Expected at least 2 CSV files matching 'table_NNN.csv' in {TABLES_DIR}, "
        f"found: {[os.path.basename(p) for p in glob.glob(os.path.join(TABLES_DIR, '*.csv'))]}"
    )
    for name in ("table_001.csv", "table_002.csv"):
        full = os.path.join(TABLES_DIR, name)
        assert os.path.isfile(full), f"Expected {full} to exist."
        assert os.path.getsize(full) > 0, f"Expected {full} to be non-empty."
        # Must decode as UTF-8.
        with open(full, "r", encoding="utf-8") as handle:
            _ = handle.read()


def test_first_csv_contains_department_revenue_table(run_extract_tables):
    """table_001.csv must hold the Quarterly Department Revenue table."""
    path = os.path.join(TABLES_DIR, "table_001.csv")
    with open(path, "r", encoding="utf-8", newline="") as handle:
        rows = [row for row in csv.reader(handle) if any(cell.strip() for cell in row)]
    assert len(rows) >= 5, (
        f"Expected at least 5 rows (header + 4 data) in {path}, got {len(rows)}."
    )

    header_cells = [cell.strip().lower() for cell in rows[0]]
    header_joined = " ".join(header_cells)
    assert "department" in header_joined, (
        f"Expected 'department' in header row of {path}, got: {rows[0]!r}"
    )
    assert "q1" in header_joined, (
        f"Expected 'q1' (Q1 Revenue) in header row of {path}, got: {rows[0]!r}"
    )
    assert "q2" in header_joined, (
        f"Expected 'q2' (Q2 Revenue) in header row of {path}, got: {rows[0]!r}"
    )

    first_col_values = {row[0].strip().lower() for row in rows[1:] if row}
    for expected in ("engineering", "marketing", "sales", "operations"):
        assert expected in first_col_values, (
            f"Expected first-column value '{expected}' in {path}, got: {first_col_values!r}"
        )

    engineering_row = next(
        (row for row in rows[1:] if row and row[0].strip().lower() == "engineering"),
        None,
    )
    assert engineering_row is not None, (
        f"Expected to find an 'Engineering' row in {path}."
    )
    assert len(engineering_row) >= 3, (
        f"Expected the Engineering row in {path} to have at least 3 columns, got: {engineering_row!r}"
    )
    q1 = _parse_int_cell(engineering_row[1])
    q2 = _parse_int_cell(engineering_row[2])
    assert q1 == 100000, f"Expected Engineering Q1 to be 100000 in {path}, got {q1}."
    assert q2 == 150000, f"Expected Engineering Q2 to be 150000 in {path}, got {q2}."


def test_second_csv_contains_top_selling_products_table(run_extract_tables):
    """table_002.csv must hold the Top Selling Products table."""
    path = os.path.join(TABLES_DIR, "table_002.csv")
    with open(path, "r", encoding="utf-8", newline="") as handle:
        rows = [row for row in csv.reader(handle) if any(cell.strip() for cell in row)]
    assert len(rows) >= 4, (
        f"Expected at least 4 rows (header + 3 data) in {path}, got {len(rows)}."
    )

    header_cells = [cell.strip().lower() for cell in rows[0]]
    header_joined = " ".join(header_cells)
    assert "product" in header_joined, (
        f"Expected 'product' in header row of {path}, got: {rows[0]!r}"
    )
    assert "units" in header_joined, (
        f"Expected 'units' (Units Sold) in header row of {path}, got: {rows[0]!r}"
    )

    first_col_values = {row[0].strip().lower() for row in rows[1:] if row}
    for expected in ("widget", "gadget", "gizmo"):
        assert expected in first_col_values, (
            f"Expected first-column value '{expected}' in {path}, got: {first_col_values!r}"
        )

    widget_row = next(
        (row for row in rows[1:] if row and row[0].strip().lower() == "widget"),
        None,
    )
    assert widget_row is not None, (
        f"Expected to find a 'Widget' row in {path}."
    )
    assert len(widget_row) >= 2, (
        f"Expected the Widget row in {path} to have at least 2 columns, got: {widget_row!r}"
    )
    units = _parse_int_cell(widget_row[1])
    assert units == 1500, f"Expected Widget Units Sold to be 1500 in {path}, got {units}."


def test_log_contains_expected_lines(run_extract_tables, trial_id):
    """The output.log must echo the trial id, table count, and CSV file lines."""
    assert os.path.isfile(LOG_PATH), f"Expected log file {LOG_PATH} to exist."
    with open(LOG_PATH, "r", encoding="utf-8") as handle:
        log = handle.read()

    expected_trial_line = re.compile(
        rf"^Trial id:\s+{re.escape(trial_id)}\s*$", re.MULTILINE
    )
    assert expected_trial_line.search(log), (
        f"Expected a line 'Trial id: {trial_id}' in {LOG_PATH}.\nFull log:\n{log}"
    )

    count_match = re.search(r"^Tables extracted:\s+(\d+)\s*$", log, re.MULTILINE)
    assert count_match is not None, (
        f"Expected a line matching 'Tables extracted: <N>' in {LOG_PATH}.\nFull log:\n{log}"
    )
    extracted = int(count_match.group(1))
    assert extracted >= 2, (
        f"Expected 'Tables extracted' to be at least 2 in {LOG_PATH}, got {extracted}."
    )

    for csv_name in ("tables/table_001.csv", "tables/table_002.csv"):
        line_pattern = re.compile(
            rf"^CSV file:\s+{re.escape(csv_name)}\s*$", re.MULTILINE
        )
        assert line_pattern.search(log), (
            f"Expected a line 'CSV file: {csv_name}' in {LOG_PATH}.\nFull log:\n{log}"
        )
