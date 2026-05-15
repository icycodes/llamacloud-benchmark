import os
import re
import subprocess

import pytest

PROJECT_DIR = "/home/user/screenshot_task"
SCRIPT_PATH = os.path.join(PROJECT_DIR, "save_screenshots.py")
SCREENSHOT_DIR = os.path.join(PROJECT_DIR, "screenshots")
LOG_PATH = os.path.join(PROJECT_DIR, "output.log")
TRIAL_ID_PATH = "/logs/artifacts/trial_id"

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
EXPECTED_FILES = ["page_01.png", "page_02.png", "page_03.png"]


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
def script_run(trial_id: str):
    """Run save_screenshots.py once and yield (log_text, job_id)."""
    assert os.path.isfile(SCRIPT_PATH), (
        f"Expected the executor-created script at {SCRIPT_PATH}, but it is missing."
    )

    # Clean up any pre-existing artifacts so we check the new run.
    if os.path.exists(LOG_PATH):
        os.remove(LOG_PATH)
    if os.path.isdir(SCREENSHOT_DIR):
        for fname in os.listdir(SCREENSHOT_DIR):
            try:
                os.remove(os.path.join(SCREENSHOT_DIR, fname))
            except OSError:
                pass
        try:
            os.rmdir(SCREENSHOT_DIR)
        except OSError:
            pass

    env = os.environ.copy()
    result = subprocess.run(
        ["python3", "save_screenshots.py"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        env=env,
        timeout=900,
    )
    assert result.returncode == 0, (
        "save_screenshots.py did not exit with status 0.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )

    assert os.path.isfile(LOG_PATH), (
        f"Expected output log at {LOG_PATH} after running save_screenshots.py."
    )
    with open(LOG_PATH, "r", encoding="utf-8") as fp:
        log_text = fp.read()

    job_id_match = re.search(
        r"^Parse job id:\s*([0-9a-zA-Z][0-9a-zA-Z\-_]*)\s*$", log_text, re.MULTILINE
    )
    assert job_id_match, (
        "Expected a line matching '^Parse job id: <id>$' in output.log. "
        f"Got: {log_text!r}"
    )
    yield log_text, job_id_match.group(1)


def test_script_uses_llama_cloud_sdk():
    with open(SCRIPT_PATH, "r", encoding="utf-8") as fp:
        source = fp.read()
    assert ("from llama_cloud" in source) or ("import llama_cloud" in source), (
        "save_screenshots.py must import from the llama_cloud Python SDK "
        "(expected 'from llama_cloud' or 'import llama_cloud')."
    )


def test_script_configures_screenshot_output():
    with open(SCRIPT_PATH, "r", encoding="utf-8") as fp:
        source = fp.read()
    assert "images_to_save" in source, (
        "save_screenshots.py must wire the LlamaParse screenshot output option "
        "(expected literal substring 'images_to_save')."
    )


def test_script_requests_images_content_metadata():
    with open(SCRIPT_PATH, "r", encoding="utf-8") as fp:
        source = fp.read()
    assert "images_content_metadata" in source, (
        "save_screenshots.py must request the images_content_metadata expand value "
        "to obtain presigned download URLs (expected literal substring "
        "'images_content_metadata')."
    )


def test_screenshot_directory_exists(script_run):
    assert os.path.isdir(SCREENSHOT_DIR), (
        f"Expected screenshot directory at {SCREENSHOT_DIR} after running the script."
    )


def test_screenshot_directory_contains_only_expected_files(script_run):
    actual = sorted(os.listdir(SCREENSHOT_DIR))
    expected = sorted(EXPECTED_FILES)
    assert actual == expected, (
        f"Screenshot directory {SCREENSHOT_DIR} must contain exactly "
        f"{expected}, but found {actual}."
    )


@pytest.mark.parametrize("filename", EXPECTED_FILES)
def test_screenshot_file_is_valid_png(script_run, filename: str):
    path = os.path.join(SCREENSHOT_DIR, filename)
    assert os.path.isfile(path), f"Missing screenshot file: {path}"
    size = os.path.getsize(path)
    assert size >= 1024, (
        f"Screenshot file {path} is suspiciously small ({size} bytes); "
        "expected at least 1024 bytes for a real page screenshot."
    )
    with open(path, "rb") as fp:
        header = fp.read(8)
    assert header == PNG_SIGNATURE, (
        f"Screenshot file {path} does not start with the canonical PNG signature; "
        f"got {header!r}."
    )


def test_log_contains_trial_id(script_run, trial_id: str):
    log_text, _ = script_run
    pattern = re.compile(rf"^Trial id:\s*{re.escape(trial_id)}\s*$", re.MULTILINE)
    assert pattern.search(log_text), (
        f"Expected a line 'Trial id: {trial_id}' in {LOG_PATH}. "
        f"Got: {log_text!r}"
    )


def test_log_contains_screenshot_count(script_run):
    log_text, _ = script_run
    assert re.search(r"^Screenshot count:\s*3\s*$", log_text, re.MULTILINE), (
        f"Expected a line 'Screenshot count: 3' in {LOG_PATH}. "
        f"Got: {log_text!r}"
    )


@pytest.mark.parametrize("filename", EXPECTED_FILES)
def test_log_reports_each_saved_file(script_run, filename: str):
    log_text, _ = script_run
    pattern = re.compile(rf"^Saved:\s*{re.escape(filename)}\s*$", re.MULTILINE)
    assert pattern.search(log_text), (
        f"Expected a line 'Saved: {filename}' in {LOG_PATH}. "
        f"Got: {log_text!r}"
    )


def test_parse_job_completed_on_llama_cloud(script_run):
    """Use the LlamaCloud Python SDK to confirm the parse job referenced in the log."""
    _, job_id = script_run

    token = os.environ.get("LLAMA_CLOUD_API_KEY")
    assert token, "LLAMA_CLOUD_API_KEY is not set in the verifier environment."

    from llama_cloud import LlamaCloud

    client = LlamaCloud(token=token)
    page = client.parsing.list(job_ids=[job_id])
    matches = [item for item in page.items if getattr(item, "id", None) == job_id]
    assert matches, (
        f"LlamaCloud parsing job {job_id} (from output.log) was not found via "
        "client.parsing.list."
    )
    status = getattr(matches[0], "status", None)
    assert status == "COMPLETED", (
        f"LlamaCloud parsing job {job_id} has status {status!r}; expected 'COMPLETED'."
    )
