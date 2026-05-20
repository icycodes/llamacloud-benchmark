import os
import re
import subprocess

import pytest

PROJECT_DIR = "/home/user/prompted_parse_task"
PARSE_SCRIPT = os.path.join(PROJECT_DIR, "parse_with_prompt.py")
OUTPUT_MD = os.path.join(PROJECT_DIR, "output.md")
OUTPUT_LOG = os.path.join(PROJECT_DIR, "output.log")
TRIAL_ID_PATH = "/logs/artifacts/trial_id"


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


def test_script_exists():
    assert os.path.isfile(PARSE_SCRIPT), (
        f"Expected the executor-created script at {PARSE_SCRIPT}, but it is missing."
    )


def test_script_uses_llama_cloud_sdk():
    """The script must import from the official LlamaCloud Python SDK."""
    with open(PARSE_SCRIPT, "r", encoding="utf-8") as fp:
        source = fp.read()
    assert ("from llama_cloud" in source) or ("import llama_cloud" in source), (
        f"{PARSE_SCRIPT} must import from the official `llama_cloud` Python SDK. "
        "Expected substring 'from llama_cloud' or 'import llama_cloud'."
    )


def test_script_wires_custom_prompt():
    """The script must reference custom_prompt to wire the LlamaParse prompt."""
    with open(PARSE_SCRIPT, "r", encoding="utf-8") as fp:
        source = fp.read()
    assert "custom_prompt" in source, (
        f"{PARSE_SCRIPT} must include the literal substring 'custom_prompt' "
        "to wire a natural-language prompt into the LlamaParse job."
    )


@pytest.fixture(scope="module")
def script_artifacts():
    """Run parse_with_prompt.py once, then yield the produced (md, log) text pair."""
    assert os.path.isfile(PARSE_SCRIPT), (
        f"Expected the executor-created script at {PARSE_SCRIPT}, but it is missing."
    )

    for path in (OUTPUT_MD, OUTPUT_LOG):
        if os.path.exists(path):
            os.remove(path)

    env = os.environ.copy()
    result = subprocess.run(
        ["python3", "parse_with_prompt.py"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        env=env,
        timeout=600,
    )
    assert result.returncode == 0, (
        "parse_with_prompt.py did not exit with status 0.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )

    assert os.path.isfile(OUTPUT_MD), (
        f"Expected markdown output at {OUTPUT_MD} after running parse_with_prompt.py, but it is missing."
    )
    assert os.path.isfile(OUTPUT_LOG), (
        f"Expected log file at {OUTPUT_LOG} after running parse_with_prompt.py, but it is missing."
    )

    with open(OUTPUT_MD, "rb") as fp:
        md_raw = fp.read()
    assert len(md_raw) > 0, f"Markdown output {OUTPUT_MD} is empty."
    try:
        md_text = md_raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        pytest.fail(f"Markdown output {OUTPUT_MD} is not valid UTF-8: {exc}")

    with open(OUTPUT_LOG, "rb") as fp:
        log_raw = fp.read()
    assert len(log_raw) > 0, f"Log file {OUTPUT_LOG} is empty."
    try:
        log_text = log_raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        pytest.fail(f"Log file {OUTPUT_LOG} is not valid UTF-8: {exc}")

    return md_text, log_text


@pytest.fixture(scope="module")
def markdown_text(script_artifacts):
    return script_artifacts[0]


@pytest.fixture(scope="module")
def log_text(script_artifacts):
    return script_artifacts[1]


@pytest.mark.parametrize(
    "item_name",
    ["Big Mac Meal", "Snack Oreo McFlurry", "Happy Meal 6 Pc"],
)
def test_markdown_contains_line_item(markdown_text: str, item_name: str):
    """The markdown output must mention every seeded line-item name."""
    assert item_name.lower() in markdown_text.lower(), (
        f"Expected line-item name '{item_name}' to appear in the markdown output. "
        f"First 800 chars of markdown: {markdown_text[:800]!r}"
    )


@pytest.mark.parametrize(
    "price",
    ["8.99", "2.69", "4.89"],
)
def test_markdown_contains_line_item_price(markdown_text: str, price: str):
    """The markdown output must mention every seeded line-item price."""
    assert price in markdown_text, (
        f"Expected line-item price '{price}' to appear in the markdown output. "
        f"First 800 chars of markdown: {markdown_text[:800]!r}"
    )


def test_markdown_contains_final_total(markdown_text: str):
    """The markdown output must surface the final Total ($17.36) of the seeded receipt."""
    assert "17.36" in markdown_text, (
        f"Expected the final Total '17.36' to appear in the markdown output. "
        f"First 800 chars of markdown: {markdown_text[:800]!r}"
    )


def test_log_contains_trial_id_line(log_text: str, trial_id: str):
    expected_line = f"Trial id: {trial_id}"
    assert any(line.strip() == expected_line for line in log_text.splitlines()), (
        f"Expected line '{expected_line}' in {OUTPUT_LOG}.\n"
        f"Log content (first 500 chars): {log_text[:500]!r}"
    )


def test_log_contains_custom_prompt_line(log_text: str):
    """The log must echo the custom prompt that was sent to the parser."""
    pattern = re.compile(r"^Custom prompt:\s*(.+)$", re.MULTILINE)
    match = pattern.search(log_text)
    assert match is not None, (
        f"Expected a 'Custom prompt: <prompt>' line in {OUTPUT_LOG}.\n"
        f"Log content (first 500 chars): {log_text[:500]!r}"
    )
    assert match.group(1).strip(), (
        "The custom prompt logged in output.log must be non-empty."
    )


@pytest.fixture(scope="module")
def parse_job_id(log_text: str) -> str:
    pattern = re.compile(r"^Parse job id:\s*([0-9a-fA-F-]+)\s*$", re.MULTILINE)
    match = pattern.search(log_text)
    assert match is not None, (
        f"Expected a 'Parse job id: <job_id>' line in {OUTPUT_LOG}.\n"
        f"Log content (first 500 chars): {log_text[:500]!r}"
    )
    job_id = match.group(1).strip()
    assert job_id, "Parsed job id from output.log must be non-empty."
    return job_id


def test_parse_job_completed_on_llama_cloud(parse_job_id: str):
    """Use the LlamaCloud Python SDK to confirm the parse job completed."""
    token = os.environ.get("LLAMA_CLOUD_API_KEY")
    assert token, "LLAMA_CLOUD_API_KEY is not set in the verifier environment."

    from llama_cloud import LlamaCloud

    client = LlamaCloud()
    page = client.parsing.list(job_ids=[parse_job_id])
    items = list(getattr(page, "items", []) or [])
    matches = [it for it in items if getattr(it, "id", None) == parse_job_id]
    assert matches, (
        f"LlamaCloud parsing job {parse_job_id} was not found via the SDK. "
        f"Returned items: {items!r}"
    )
    status = getattr(matches[0], "status", None)
    assert status == "COMPLETED", (
        f"Expected LlamaCloud parse job {parse_job_id} status 'COMPLETED', got {status!r}."
    )
