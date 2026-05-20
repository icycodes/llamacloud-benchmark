import os
import subprocess
import sys

import pytest

PROJECT_DIR = "/home/user/myproject"
SYNC_SCRIPT = os.path.join(PROJECT_DIR, "sync.py")
DATA_DIR = os.path.join(PROJECT_DIR, "data")
ALPHA_PATH = os.path.join(DATA_DIR, "alpha.txt")
BETA_PATH = os.path.join(DATA_DIR, "beta.txt")
GAMMA_PATH = os.path.join(DATA_DIR, "gamma.txt")
TRIAL_ID_PATH = "/logs/artifacts/trial_id"
PROJECT_NAME = "Default"


def _read_trial_id() -> str:
    with open(TRIAL_ID_PATH, "r", encoding="utf-8") as f:
        return f.read().strip()


def _index_name() -> str:
    return f"llama-sync-{_read_trial_id()}"


def _run_sync_cli() -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            sys.executable,
            SYNC_SCRIPT,
            "--folder",
            DATA_DIR,
            "--index",
            _index_name(),
            "--project",
            PROJECT_NAME,
        ],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
        env=os.environ.copy(),
        timeout=900,
    )


def _last_non_empty_line(text: str) -> str:
    for line in reversed(text.splitlines()):
        if line.strip():
            return line.strip()
    return ""


def _list_pipeline_file_names() -> list:
    from llama_cloud_services import LlamaCloudIndex

    index = LlamaCloudIndex(
        name=_index_name(),
        project_name=PROJECT_NAME,
    )
    pipeline_id = index.pipeline.id
    client = index._client
    files = list(client.pipelines.list_pipeline_files(pipeline_id=pipeline_id))
    names = [getattr(f, "name", None) for f in files]
    return [n for n in names if n]


def _cleanup_gamma_if_present():
    if os.path.isfile(GAMMA_PATH):
        os.remove(GAMMA_PATH)


@pytest.fixture(scope="module")
def first_run_result():
    # Pre-clean any gamma.txt left from a previous trial.
    _cleanup_gamma_if_present()
    return _run_sync_cli()


def test_sync_script_exists(first_run_result):
    assert os.path.isfile(SYNC_SCRIPT), (
        f"Expected the sync CLI at {SYNC_SCRIPT}."
    )


def test_first_run_exits_successfully(first_run_result):
    assert first_run_result.returncode == 0, (
        "Expected the first sync run to exit with code 0. "
        f"stdout={first_run_result.stdout!r}, "
        f"stderr={first_run_result.stderr!r}"
    )


def test_first_run_reports_two_new_files(first_run_result):
    last_line = _last_non_empty_line(first_run_result.stdout)
    expected = "Uploaded 2 new file(s): alpha.txt, beta.txt"
    assert last_line == expected, (
        f"Expected the last stdout line to be {expected!r}; "
        f"got {last_line!r}. Full stdout: {first_run_result.stdout!r}"
    )


def test_index_contains_seeded_files_after_first_run(first_run_result):
    assert first_run_result.returncode == 0, (
        "Skipping cloud-side check because the first sync run did not "
        "succeed."
    )
    names = _list_pipeline_file_names()
    for required in ("alpha.txt", "beta.txt"):
        assert required in names, (
            f"Expected the LlamaCloud index '{_index_name()}' to contain "
            f"a file named {required!r}; got files: {names!r}."
        )


@pytest.fixture(scope="module")
def second_run_result(first_run_result):
    assert first_run_result.returncode == 0, (
        "Skipping the idempotency run because the first run failed."
    )
    return _run_sync_cli()


def test_second_run_exits_successfully(second_run_result):
    assert second_run_result.returncode == 0, (
        "Expected the second (idempotent) sync run to exit with code 0. "
        f"stdout={second_run_result.stdout!r}, "
        f"stderr={second_run_result.stderr!r}"
    )


def test_second_run_reports_zero_new_files(second_run_result):
    last_line = _last_non_empty_line(second_run_result.stdout)
    expected = "Uploaded 0 new file(s): none"
    assert last_line == expected, (
        "Expected the second run to be idempotent and report 0 new "
        f"uploads. Wanted last stdout line {expected!r}, got "
        f"{last_line!r}. Full stdout: {second_run_result.stdout!r}"
    )


def test_index_has_no_duplicate_seeded_files_after_second_run(second_run_result):
    names = _list_pipeline_file_names()
    for required in ("alpha.txt", "beta.txt"):
        assert names.count(required) == 1, (
            "Expected exactly one copy of "
            f"{required!r} in the LlamaCloud index after the idempotent "
            f"run; got file list: {names!r}."
        )


@pytest.fixture(scope="module")
def third_run_result(second_run_result):
    assert second_run_result.returncode == 0, (
        "Skipping the additive run because the idempotent run failed."
    )
    with open(GAMMA_PATH, "w", encoding="utf-8") as f:
        f.write("Gamma test content for incremental ingestion.\n")
    return _run_sync_cli()


def test_third_run_exits_successfully(third_run_result):
    assert third_run_result.returncode == 0, (
        "Expected the third sync run (after adding gamma.txt) to exit "
        "with code 0. "
        f"stdout={third_run_result.stdout!r}, "
        f"stderr={third_run_result.stderr!r}"
    )


def test_third_run_reports_only_gamma_uploaded(third_run_result):
    last_line = _last_non_empty_line(third_run_result.stdout)
    expected = "Uploaded 1 new file(s): gamma.txt"
    assert last_line == expected, (
        "Expected the third run to upload only the new file. "
        f"Wanted last stdout line {expected!r}, got "
        f"{last_line!r}. Full stdout: {third_run_result.stdout!r}"
    )


def test_index_contains_all_three_files_after_third_run(third_run_result):
    names = _list_pipeline_file_names()
    for required in ("alpha.txt", "beta.txt", "gamma.txt"):
        assert required in names, (
            f"Expected the LlamaCloud index '{_index_name()}' to contain "
            f"a file named {required!r} after the additive run; "
            f"got files: {names!r}."
        )
