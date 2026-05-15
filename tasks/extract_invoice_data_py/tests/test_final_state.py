import json
import os
import re
import subprocess

import pytest

PROJECT_DIR = "/home/user/extract_task"
EXTRACT_SCRIPT = os.path.join(PROJECT_DIR, "extract.py")
OUTPUT_JSON = os.path.join(PROJECT_DIR, "output.json")
OUTPUT_LOG = os.path.join(PROJECT_DIR, "output.log")
TRIAL_ID_PATH = "/logs/artifacts/trial_id"

EXPECTED_KEYS = {
    "invoice_number",
    "vendor_name",
    "customer_name",
    "total_amount",
    "currency",
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


@pytest.fixture(scope="module")
def expected_external_file_id(trial_id: str) -> str:
    return f"harbor-invoice-{trial_id}.pdf"


@pytest.fixture(scope="module")
def script_run():
    """Run extract.py once and yield (output_json_text, output_log_text)."""
    assert os.path.isfile(EXTRACT_SCRIPT), (
        f"Expected the executor-created script at {EXTRACT_SCRIPT}, but it is missing."
    )

    for path in (OUTPUT_JSON, OUTPUT_LOG):
        if os.path.exists(path):
            os.remove(path)

    env = os.environ.copy()
    result = subprocess.run(
        ["python3", "extract.py"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        env=env,
        timeout=900,
    )
    assert result.returncode == 0, (
        "extract.py did not exit with status 0.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )

    assert os.path.isfile(OUTPUT_JSON), (
        f"Expected output JSON at {OUTPUT_JSON} after running extract.py, but it is missing."
    )
    assert os.path.isfile(OUTPUT_LOG), (
        f"Expected output log at {OUTPUT_LOG} after running extract.py, but it is missing."
    )

    with open(OUTPUT_JSON, "rb") as fp:
        json_raw = fp.read()
    assert len(json_raw) > 0, f"Output JSON {OUTPUT_JSON} is empty."
    try:
        json_text = json_raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        pytest.fail(f"Output JSON {OUTPUT_JSON} is not valid UTF-8: {exc}")

    with open(OUTPUT_LOG, "r", encoding="utf-8") as fp:
        log_text = fp.read()

    return json_text, log_text


@pytest.fixture(scope="module")
def extracted(script_run):
    """Parse output.json and return the top-level dict."""
    json_text, _ = script_run
    try:
        data = json.loads(json_text)
    except json.JSONDecodeError as exc:
        pytest.fail(
            f"Output JSON {OUTPUT_JSON} is not valid JSON: {exc}\n"
            f"First 500 chars: {json_text[:500]!r}"
        )
    assert isinstance(data, dict), (
        f"Top level of {OUTPUT_JSON} must be a JSON object, got {type(data).__name__}."
    )
    return data


def test_output_json_has_exact_top_level_keys(extracted):
    keys = set(extracted.keys())
    assert keys == EXPECTED_KEYS, (
        f"Top-level keys of {OUTPUT_JSON} must be exactly {sorted(EXPECTED_KEYS)} "
        f"(no wrapper fields like 'data' or 'result'). Got: {sorted(keys)}"
    )


def test_extracted_invoice_number(extracted):
    invoice_number = extracted.get("invoice_number")
    assert isinstance(invoice_number, str), (
        f"'invoice_number' must be a string in {OUTPUT_JSON}, got {type(invoice_number).__name__}."
    )
    assert invoice_number == "INV-2024-7842", (
        f"Expected invoice_number to be 'INV-2024-7842', got {invoice_number!r}."
    )


def test_extracted_vendor_name(extracted):
    vendor_name = extracted.get("vendor_name")
    assert isinstance(vendor_name, str), (
        f"'vendor_name' must be a string in {OUTPUT_JSON}, got {type(vendor_name).__name__}."
    )
    assert "pochi industries" in vendor_name.lower(), (
        f"Expected vendor_name to contain 'Pochi Industries' (case-insensitive), got {vendor_name!r}."
    )


def test_extracted_customer_name(extracted):
    customer_name = extracted.get("customer_name")
    assert isinstance(customer_name, str), (
        f"'customer_name' must be a string in {OUTPUT_JSON}, got {type(customer_name).__name__}."
    )
    assert "atlantis trading" in customer_name.lower(), (
        f"Expected customer_name to contain 'Atlantis Trading' (case-insensitive), got {customer_name!r}."
    )


def test_extracted_total_amount(extracted):
    total = extracted.get("total_amount")
    assert isinstance(total, (int, float)) and not isinstance(total, bool), (
        f"'total_amount' must be a number in {OUTPUT_JSON}, got {type(total).__name__} value {total!r}."
    )
    assert abs(float(total) - 6480.0) <= 0.01, (
        f"Expected total_amount to be 6480.00 (+/- 0.01), got {total!r}."
    )


def test_extracted_currency(extracted):
    currency = extracted.get("currency")
    assert isinstance(currency, str), (
        f"'currency' must be a string in {OUTPUT_JSON}, got {type(currency).__name__}."
    )
    assert currency.strip().upper() == "USD", (
        f"Expected currency to be 'USD' (case-insensitive), got {currency!r}."
    )


def test_output_log_contains_extract_job_id_line(script_run):
    _, log_text = script_run
    match = re.search(r"^Extract job id:\s+(\S+)\s*$", log_text, re.MULTILINE)
    assert match is not None, (
        f"Expected a line matching 'Extract job id: <job_id>' in {OUTPUT_LOG}.\n"
        f"First 500 chars of log: {log_text[:500]!r}"
    )


def test_extract_job_completed_on_llama_cloud(script_run):
    """Use the LlamaCloud SDK to confirm the recorded job exists and COMPLETED."""
    _, log_text = script_run
    match = re.search(r"^Extract job id:\s+(\S+)\s*$", log_text, re.MULTILINE)
    assert match is not None, (
        f"No 'Extract job id:' line found in {OUTPUT_LOG}; cannot verify job."
    )
    job_id = match.group(1)

    token = os.environ.get("LLAMA_CLOUD_API_KEY")
    assert token, "LLAMA_CLOUD_API_KEY is not set in the verifier environment."

    from llama_cloud import LlamaCloud

    client = LlamaCloud(token=token)
    job = client.extract.get(job_id)
    status = getattr(job, "status", None)
    assert status == "COMPLETED", (
        f"Expected LlamaCloud extract job {job_id!r} to be COMPLETED, got status={status!r}."
    )


def test_external_file_id_registered_on_llama_cloud(script_run, expected_external_file_id):
    """The uploaded LlamaCloud file must use the trial-scoped external_file_id."""
    token = os.environ.get("LLAMA_CLOUD_API_KEY")
    assert token, "LLAMA_CLOUD_API_KEY is not set in the verifier environment."

    from llama_cloud import LlamaCloud

    client = LlamaCloud(token=token)

    found = False
    # The SDK's files.list returns either a paginated wrapper or an iterable.
    # Iterate defensively to handle both shapes.
    try:
        listing = client.files.list(external_file_id=expected_external_file_id)
    except TypeError:
        # Some SDK versions do not accept external_file_id as a filter; fall back to scanning.
        listing = client.files.list()

    items = getattr(listing, "items", None)
    iterable = items if items is not None else listing
    for f in iterable:
        if getattr(f, "external_file_id", None) == expected_external_file_id:
            found = True
            break
        # Pagination handling for SDK list shapes
        if found:
            break

    if not found:
        # Try paginating manually if available.
        next_page = getattr(listing, "get_next_page", None)
        page = listing
        for _ in range(20):  # cap to avoid infinite loops
            if not callable(getattr(page, "has_next_page", None)) or not page.has_next_page():
                break
            page = page.get_next_page()
            for f in getattr(page, "items", []) or []:
                if getattr(f, "external_file_id", None) == expected_external_file_id:
                    found = True
                    break
            if found:
                break

    assert found, (
        f"Could not find a LlamaCloud file with external_file_id="
        f"{expected_external_file_id!r}. The executor must upload the invoice using that "
        "trial-scoped identifier."
    )
