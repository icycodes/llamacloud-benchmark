import json
import os
import re
import subprocess

import pytest

PROJECT_DIR = "/home/user/myproject"
SCRIPT_PATH = os.path.join(PROJECT_DIR, "extract_invoice.py")
SAMPLE_PDF = os.path.join(PROJECT_DIR, "invoice.pdf")
OUTPUT_JSON = os.path.join(PROJECT_DIR, "invoice.json")
OUTPUT_LOG = os.path.join(PROJECT_DIR, "output.log")
TRIAL_ID_PATH = "/logs/artifacts/trial_id"

EXPECTED_INVOICE_NUMBER = "INV-2024-0042"
EXPECTED_TOTAL = 1846.80
TOTAL_TOLERANCE = 0.05


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
        timeout=900,
    )
    yield completed


def _load_invoice_json():
    with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def test_script_exit_code_is_zero(run_agent_script):
    """The agent's extract_invoice.py must run to completion with exit code 0."""
    completed = run_agent_script
    assert completed.returncode == 0, (
        f"extract_invoice.py exited with non-zero status {completed.returncode}.\n"
        f"STDOUT:\n{completed.stdout}\n"
        f"STDERR:\n{completed.stderr}"
    )


def test_output_json_file_exists():
    """The invoice JSON output file must exist and be non-empty."""
    assert os.path.isfile(OUTPUT_JSON), (
        f"Expected JSON output file at {OUTPUT_JSON} to be created by the script."
    )
    assert os.path.getsize(OUTPUT_JSON) > 0, (
        f"JSON output file {OUTPUT_JSON} exists but is empty."
    )


def test_output_json_top_level_shape():
    """invoice.json must be valid JSON with the required top-level keys."""
    try:
        data = _load_invoice_json()
    except json.JSONDecodeError as exc:
        pytest.fail(f"{OUTPUT_JSON} is not valid JSON: {exc}")
    assert isinstance(data, dict), (
        f"Expected {OUTPUT_JSON} top level to be a JSON object, got "
        f"{type(data).__name__}."
    )
    for key in ("trial_id", "job_id", "status", "data"):
        assert key in data, (
            f"Expected key `{key}` to be present in {OUTPUT_JSON}. "
            f"Top-level keys present: {sorted(data.keys())!r}"
        )


def test_output_json_trial_id_matches():
    """The `trial_id` in invoice.json must match the harness `trial_id` value."""
    data = _load_invoice_json()
    expected = _read_trial_id()
    assert data.get("trial_id") == expected, (
        f"Expected invoice.json `trial_id` to equal `{expected}` "
        f"(from {TRIAL_ID_PATH}), got `{data.get('trial_id')!r}`."
    )


def test_output_json_job_id_is_non_empty_string():
    """The `job_id` must be a non-empty string."""
    data = _load_invoice_json()
    job_id = data.get("job_id")
    assert isinstance(job_id, str) and job_id.strip(), (
        f"Expected `job_id` in {OUTPUT_JSON} to be a non-empty string, "
        f"got {type(job_id).__name__}: {job_id!r}."
    )


def test_output_json_status_is_completed():
    """The `status` must equal the string `COMPLETED`."""
    data = _load_invoice_json()
    status = data.get("status")
    assert status == "COMPLETED", (
        f"Expected `status` in {OUTPUT_JSON} to equal `COMPLETED`, got {status!r}."
    )


def test_output_json_data_is_object():
    """The `data` field must be a JSON object (not a list, not null)."""
    data = _load_invoice_json()
    extracted = data.get("data")
    assert isinstance(extracted, dict), (
        f"Expected `data` in {OUTPUT_JSON} to be a JSON object (dict), got "
        f"{type(extracted).__name__}: {extracted!r}. The task requires storing "
        "a single per-doc result, not the full list returned by the SDK."
    )


def test_extracted_invoice_number_matches():
    """`data.invoice_number` must equal INV-2024-0042 (case-insensitive)."""
    data = _load_invoice_json()
    extracted = data["data"]
    invoice_number = extracted.get("invoice_number")
    assert isinstance(invoice_number, str), (
        f"Expected `data.invoice_number` to be a string, got "
        f"{type(invoice_number).__name__}: {invoice_number!r}."
    )
    assert invoice_number.strip().lower() == EXPECTED_INVOICE_NUMBER.lower(), (
        f"Expected `data.invoice_number` to equal `{EXPECTED_INVOICE_NUMBER}` "
        f"(case-insensitive), got `{invoice_number!r}`."
    )


def test_extracted_vendor_name_contains_acme():
    """`data.vendor_name` must contain the substring `Acme` (case-insensitive)."""
    data = _load_invoice_json()
    vendor_name = data["data"].get("vendor_name")
    assert isinstance(vendor_name, str) and vendor_name.strip(), (
        f"Expected `data.vendor_name` to be a non-empty string, got "
        f"{type(vendor_name).__name__}: {vendor_name!r}."
    )
    assert "acme" in vendor_name.lower(), (
        f"Expected `data.vendor_name` to contain `Acme` (case-insensitive), "
        f"got `{vendor_name!r}`."
    )


def test_extracted_customer_name_contains_globex():
    """`data.customer_name` must contain the substring `Globex` (case-insensitive)."""
    data = _load_invoice_json()
    customer_name = data["data"].get("customer_name")
    assert isinstance(customer_name, str) and customer_name.strip(), (
        f"Expected `data.customer_name` to be a non-empty string, got "
        f"{type(customer_name).__name__}: {customer_name!r}."
    )
    assert "globex" in customer_name.lower(), (
        f"Expected `data.customer_name` to contain `Globex` (case-insensitive), "
        f"got `{customer_name!r}`."
    )


def test_extracted_total_within_tolerance():
    """`data.total`, parsed as a number, must be within 0.05 of 1846.80."""
    data = _load_invoice_json()
    raw_total = data["data"].get("total")
    assert raw_total is not None, "`data.total` is missing from the extracted result."
    try:
        total = float(raw_total)
    except (TypeError, ValueError) as exc:
        pytest.fail(
            f"`data.total` ({raw_total!r}) could not be parsed as a number: {exc}"
        )
    assert abs(total - EXPECTED_TOTAL) <= TOTAL_TOLERANCE, (
        f"Expected `data.total` to be within {TOTAL_TOLERANCE} of "
        f"{EXPECTED_TOTAL}, got {total}."
    )


def test_extracted_line_items_cover_expected_descriptions():
    """`data.line_items` must be a list of >=3 entries covering all expected descriptions."""
    data = _load_invoice_json()
    line_items = data["data"].get("line_items")
    assert isinstance(line_items, list), (
        f"Expected `data.line_items` to be a list, got "
        f"{type(line_items).__name__}: {line_items!r}."
    )
    assert len(line_items) >= 3, (
        f"Expected at least 3 line items, got {len(line_items)}."
    )
    descriptions = []
    for idx, item in enumerate(line_items):
        assert isinstance(item, dict), (
            f"Expected `data.line_items[{idx}]` to be a dict, got "
            f"{type(item).__name__}."
        )
        desc = item.get("description")
        assert isinstance(desc, str), (
            f"Expected `data.line_items[{idx}].description` to be a string, got "
            f"{type(desc).__name__}: {desc!r}."
        )
        descriptions.append(desc.lower())
    combined = " | ".join(descriptions)
    for needle in ("widget type a", "onsite support", "annual maintenance"):
        assert needle in combined, (
            f"Expected the combined `data.line_items[*].description` text to "
            f"contain `{needle}` (case-insensitive), but it was missing. "
            f"Combined descriptions: {combined!r}"
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


def test_output_log_contains_job_status_line():
    """The log file must contain a `job_status: COMPLETED` line."""
    with open(OUTPUT_LOG, "r", encoding="utf-8") as f:
        log_content = f.read()
    pattern = re.compile(r"^\s*job_status\s*:\s*COMPLETED\s*$", re.MULTILINE)
    assert pattern.search(log_content), (
        f"Expected {OUTPUT_LOG} to contain a line `job_status: COMPLETED`, but "
        f"none was found.\nLog content:\n{log_content!r}"
    )


def test_output_log_contains_invoice_number_line():
    """The log file must contain `invoice_number: INV-2024-0042` (case-insensitive)."""
    with open(OUTPUT_LOG, "r", encoding="utf-8") as f:
        log_content = f.read()
    pattern = re.compile(
        r"^\s*invoice_number\s*:\s*" + re.escape(EXPECTED_INVOICE_NUMBER) + r"\s*$",
        re.MULTILINE | re.IGNORECASE,
    )
    assert pattern.search(log_content), (
        f"Expected {OUTPUT_LOG} to contain a line "
        f"`invoice_number: {EXPECTED_INVOICE_NUMBER}` (case-insensitive on the "
        f"value), but no such line was found.\nLog content:\n{log_content!r}"
    )


def test_output_log_contains_total_line_within_tolerance():
    """The log file must contain a `total: <number>` line within 0.05 of 1846.80."""
    with open(OUTPUT_LOG, "r", encoding="utf-8") as f:
        log_content = f.read()
    match = re.search(
        r"^\s*total\s*:\s*([-+]?\d+(?:\.\d+)?)\s*$",
        log_content,
        re.MULTILINE,
    )
    assert match, (
        f"Expected {OUTPUT_LOG} to contain a line matching `total: <number>`, "
        f"but none was found.\nLog content:\n{log_content!r}"
    )
    value = float(match.group(1))
    assert abs(value - EXPECTED_TOTAL) <= TOTAL_TOLERANCE, (
        f"Expected the `total:` line to be within {TOTAL_TOLERANCE} of "
        f"{EXPECTED_TOTAL}, got {value}."
    )
