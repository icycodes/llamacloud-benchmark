import json
import os
import re
import subprocess

import pytest


PROJECT_DIR = "/home/user/extract_task"
SCRIPT_PATH = os.path.join(PROJECT_DIR, "extract.py")
OUTPUT_JSON = os.path.join(PROJECT_DIR, "output.json")
OUTPUT_LOG = os.path.join(PROJECT_DIR, "output.log")
TRIAL_ID_PATH = "/logs/artifacts/trial_id"

EXPECTED_INVOICE_NUMBER = "INV-2024-7788"
EXPECTED_CUSTOMER_EMAIL = "billing@globex.example"
EXPECTED_LINE_ITEMS = ["widget a", "gadget b", "service c", "license d"]
EXPECTED_TOTAL_AMOUNT = 425.0


def _read_trial_id() -> str:
    """Read the trial id used to scope this verification run."""
    assert os.path.isfile(TRIAL_ID_PATH), (
        f"Expected trial id file at {TRIAL_ID_PATH} to be present in the verifier environment."
    )
    with open(TRIAL_ID_PATH, "r", encoding="utf-8") as fh:
        return fh.read().strip()


@pytest.fixture(scope="session")
def trial_id() -> str:
    return _read_trial_id()


@pytest.fixture(scope="session")
def run_script():
    """Pre-clean any output artifacts and run the executor's extract.py once for the session."""
    for path in (OUTPUT_JSON, OUTPUT_LOG):
        if os.path.exists(path):
            os.remove(path)

    assert os.path.isfile(SCRIPT_PATH), (
        f"Expected the executor to create the script at {SCRIPT_PATH}."
    )

    completed = subprocess.run(
        ["python3", "extract.py"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=300,
    )
    return completed


@pytest.fixture(scope="session")
def parsed_output(run_script):
    assert run_script.returncode == 0, (
        f"Expected `python3 extract.py` to exit with code 0, got {run_script.returncode}. "
        f"stdout=\n{run_script.stdout}\nstderr=\n{run_script.stderr}"
    )
    assert os.path.isfile(OUTPUT_JSON), (
        f"Expected the extraction output JSON to exist at {OUTPUT_JSON} after running extract.py."
    )
    assert os.path.getsize(OUTPUT_JSON) > 0, (
        f"Expected the extraction output JSON at {OUTPUT_JSON} to be non-empty."
    )
    with open(OUTPUT_JSON, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    assert isinstance(data, dict), (
        f"Expected the top-level JSON value in {OUTPUT_JSON} to be an object, got: {type(data).__name__}."
    )
    return data


def test_script_uses_llama_cloud_and_pydantic():
    """The script must use the LlamaCloud SDK and Pydantic to drive the extraction."""
    assert os.path.isfile(SCRIPT_PATH), (
        f"Expected the executor's script to exist at {SCRIPT_PATH}."
    )
    with open(SCRIPT_PATH, "r", encoding="utf-8") as fh:
        source = fh.read()
    assert "llama_cloud" in source, (
        f"Expected {SCRIPT_PATH} to reference the `llama_cloud` SDK (e.g. `from llama_cloud import LlamaCloud`)."
    )
    assert "BaseModel" in source, (
        f"Expected {SCRIPT_PATH} to define a Pydantic schema by subclassing `BaseModel`."
    )


def test_extract_script_runs_successfully(run_script):
    """Confirm the executor's script exits cleanly."""
    assert run_script.returncode == 0, (
        f"Expected `python3 extract.py` to exit with code 0, got {run_script.returncode}. "
        f"stdout=\n{run_script.stdout}\nstderr=\n{run_script.stderr}"
    )


def test_output_json_has_required_top_level_keys(parsed_output):
    required = {"invoice_number", "customer_name", "customer_email", "line_items", "total_amount"}
    missing = required - set(parsed_output.keys())
    assert not missing, (
        f"Expected {OUTPUT_JSON} to contain top-level keys {sorted(required)}; missing: {sorted(missing)}."
    )


def test_output_json_invoice_number(parsed_output):
    value = parsed_output.get("invoice_number")
    assert isinstance(value, str), (
        f"Expected `invoice_number` in {OUTPUT_JSON} to be a string, got: {type(value).__name__}."
    )
    assert value.strip().upper() == EXPECTED_INVOICE_NUMBER.upper(), (
        f"Expected `invoice_number` to equal {EXPECTED_INVOICE_NUMBER!r}, got: {value!r}."
    )


def test_output_json_customer_name(parsed_output):
    value = parsed_output.get("customer_name")
    assert isinstance(value, str), (
        f"Expected `customer_name` in {OUTPUT_JSON} to be a string, got: {type(value).__name__}."
    )
    assert "globex" in value.lower(), (
        f"Expected `customer_name` to contain 'globex' (from the source invoice), got: {value!r}."
    )


def test_output_json_customer_email(parsed_output):
    value = parsed_output.get("customer_email")
    assert isinstance(value, str), (
        f"Expected `customer_email` in {OUTPUT_JSON} to be a string, got: {type(value).__name__}."
    )
    assert value.strip().lower() == EXPECTED_CUSTOMER_EMAIL, (
        f"Expected `customer_email` to equal {EXPECTED_CUSTOMER_EMAIL!r}, got: {value!r}."
    )


def test_output_json_total_amount(parsed_output):
    value = parsed_output.get("total_amount")
    assert isinstance(value, (int, float)), (
        f"Expected `total_amount` in {OUTPUT_JSON} to be a number, got: {type(value).__name__} ({value!r})."
    )
    assert abs(float(value) - EXPECTED_TOTAL_AMOUNT) < 0.5, (
        f"Expected `total_amount` to be approximately {EXPECTED_TOTAL_AMOUNT}, got: {value!r}."
    )


def test_output_json_line_items_count_and_keys(parsed_output):
    line_items = parsed_output.get("line_items")
    assert isinstance(line_items, list), (
        f"Expected `line_items` in {OUTPUT_JSON} to be a list, got: {type(line_items).__name__}."
    )
    assert len(line_items) == 4, (
        f"Expected exactly 4 line items in {OUTPUT_JSON}, got: {len(line_items)}."
    )
    required_keys = {"item", "quantity", "unit_price", "total"}
    for idx, row in enumerate(line_items):
        assert isinstance(row, dict), (
            f"Expected `line_items[{idx}]` to be an object, got: {type(row).__name__}."
        )
        missing = required_keys - set(row.keys())
        assert not missing, (
            f"Expected `line_items[{idx}]` to contain keys {sorted(required_keys)}; missing: {sorted(missing)}."
        )


def test_output_json_line_item_names_present(parsed_output):
    line_items = parsed_output["line_items"]
    seen = {str(row.get("item", "")).strip().lower() for row in line_items}
    for expected in EXPECTED_LINE_ITEMS:
        assert any(expected in name for name in seen), (
            f"Expected to find a line item containing {expected!r} in {OUTPUT_JSON}, got items: {sorted(seen)}."
        )


def test_output_json_widget_a_row_values(parsed_output):
    line_items = parsed_output["line_items"]
    widget_rows = [row for row in line_items if "widget a" in str(row.get("item", "")).lower()]
    assert widget_rows, (
        f"Expected to find a line item whose `item` contains 'Widget A' in {OUTPUT_JSON}."
    )
    row = widget_rows[0]
    quantity = row.get("quantity")
    total = row.get("total")
    assert int(quantity) == 3, (
        f"Expected the 'Widget A' row to have quantity 3, got: {quantity!r}."
    )
    assert isinstance(total, (int, float)), (
        f"Expected the 'Widget A' row total to be a number, got: {type(total).__name__} ({total!r})."
    )
    assert abs(float(total) - 75.0) < 0.5, (
        f"Expected the 'Widget A' row total to be approximately 75.0, got: {total!r}."
    )


def test_output_log_lines(parsed_output, trial_id):
    assert os.path.isfile(OUTPUT_LOG), (
        f"Expected the human-readable log file at {OUTPUT_LOG} after running extract.py."
    )
    with open(OUTPUT_LOG, "r", encoding="utf-8") as fh:
        log_text = fh.read()

    lines = [line.rstrip() for line in log_text.splitlines()]

    expected_trial_line = f"Trial id: {trial_id}"
    assert expected_trial_line in lines, (
        f"Expected {OUTPUT_LOG} to contain a line {expected_trial_line!r}; got:\n{log_text}"
    )

    expected_invoice_line = f"Invoice number: {EXPECTED_INVOICE_NUMBER}"
    assert expected_invoice_line in lines, (
        f"Expected {OUTPUT_LOG} to contain a line {expected_invoice_line!r}; got:\n{log_text}"
    )

    expected_count_line = f"Line item count: {len(parsed_output['line_items'])}"
    assert expected_count_line in lines, (
        f"Expected {OUTPUT_LOG} to contain a line {expected_count_line!r}; got:\n{log_text}"
    )

    total_pattern = re.compile(r"^Total amount:\s*4\d{2}(?:\.\d+)?\s*$")
    assert any(total_pattern.match(line) for line in lines), (
        f"Expected {OUTPUT_LOG} to contain a line matching `^Total amount:\\s*4\\d{{2}}(?:\\.\\d+)?\\s*$`; got:\n{log_text}"
    )
