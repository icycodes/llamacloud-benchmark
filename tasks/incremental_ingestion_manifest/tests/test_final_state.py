import hashlib
import json
import os
import subprocess
import pytest

PROJECT_DIR = "/home/user/incremental_ingest"
DATA_DIR = os.path.join(PROJECT_DIR, "data")
SYNC_PY = os.path.join(PROJECT_DIR, "sync.py")
PRIOR_MANIFEST = os.path.join(PROJECT_DIR, "prior_manifest.json")
CURRENT_MANIFEST = os.path.join(PROJECT_DIR, "current_manifest.json")
UPLOAD_PLAN = os.path.join(PROJECT_DIR, "upload_plan.json")


def _sha256_of_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


@pytest.fixture(scope="module")
def sync_run():
    """Run the user's sync.py exactly once and return its CompletedProcess.

    If the agent already ran it (and the outputs are present), we still rerun so
    the verifier can validate the stdout line. Re-running is idempotent because
    sync.py overwrites the same output files.
    """
    assert os.path.isfile(SYNC_PY), (
        f"Expected {SYNC_PY} to exist before running final-state verification."
    )
    result = subprocess.run(
        ["python3", "sync.py"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=60,
    )
    return result


def test_sync_script_exists():
    assert os.path.isfile(SYNC_PY), (
        f"Expected {SYNC_PY} to be created by the agent."
    )


def test_sync_script_uses_llama_cloud_sdk():
    with open(SYNC_PY, "r", encoding="utf-8") as f:
        content = f.read()
    assert "from llama_cloud import LlamaCloud" in content, (
        f"{SYNC_PY} must contain 'from llama_cloud import LlamaCloud'."
    )


def test_sync_script_does_not_hardcode_api_key():
    with open(SYNC_PY, "r", encoding="utf-8") as f:
        content = f.read()
    assert "llx-" not in content, (
        f"{SYNC_PY} appears to hardcode a LlamaCloud API key (found 'llx-' prefix). "
        "It must rely on LLAMA_CLOUD_API_KEY from the environment."
    )


def test_sync_script_makes_no_network_calls():
    """The sanity-check should construct the client only — no real API calls."""
    with open(SYNC_PY, "r", encoding="utf-8") as f:
        content = f.read()
    forbidden = ["files.create", "pipelines.", "requests.", "urllib.request", "httpx."]
    for needle in forbidden:
        assert needle not in content, (
            f"{SYNC_PY} must not call LlamaCloud or HTTP endpoints directly. "
            f"Forbidden substring found: {needle!r}."
        )


def test_sync_script_runs_successfully(sync_run):
    assert sync_run.returncode == 0, (
        f"python3 sync.py exited with code {sync_run.returncode}. "
        f"stdout: {sync_run.stdout!r}, stderr: {sync_run.stderr!r}"
    )


def test_sync_script_prints_expected_summary(sync_run):
    expected = "added=1 modified=1 removed=1 unchanged=1"
    assert sync_run.stdout.strip() == expected, (
        f"sync.py stdout must equal {expected!r}, got: {sync_run.stdout!r}"
    )


def test_current_manifest_exists_and_valid(sync_run):
    assert os.path.isfile(CURRENT_MANIFEST), (
        f"Expected {CURRENT_MANIFEST} to be created by sync.py."
    )
    with open(CURRENT_MANIFEST, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, dict), (
        f"{CURRENT_MANIFEST} must contain a JSON object. Got: {type(data).__name__}"
    )
    assert "files" in data and isinstance(data["files"], dict), (
        f"{CURRENT_MANIFEST} must contain a 'files' object."
    )
    files = data["files"]
    expected_keys = {"intro.txt", "glossary.txt", "changelog.txt"}
    assert set(files.keys()) == expected_keys, (
        f"{CURRENT_MANIFEST} 'files' must contain exactly the keys "
        f"{sorted(expected_keys)}, got: {sorted(files.keys())}"
    )


def test_current_manifest_hashes_and_sizes(sync_run):
    with open(CURRENT_MANIFEST, "r", encoding="utf-8") as f:
        data = json.load(f)
    files = data["files"]
    for rel in ("intro.txt", "glossary.txt", "changelog.txt"):
        entry = files[rel]
        assert isinstance(entry, dict), (
            f"{CURRENT_MANIFEST}: entry for {rel!r} must be an object. Got: {entry!r}"
        )
        actual_path = os.path.join(DATA_DIR, rel)
        expected_sha = _sha256_of_file(actual_path)
        expected_size = os.path.getsize(actual_path)
        sha = entry.get("sha256")
        size = entry.get("size")
        assert isinstance(sha, str) and len(sha) == 64 and sha == sha.lower(), (
            f"{CURRENT_MANIFEST}: sha256 for {rel!r} must be a 64-char lower-case hex "
            f"string. Got: {sha!r}"
        )
        assert sha == expected_sha, (
            f"{CURRENT_MANIFEST}: sha256 mismatch for {rel!r}. "
            f"Expected {expected_sha!r}, got {sha!r}."
        )
        assert isinstance(size, int) and size == expected_size, (
            f"{CURRENT_MANIFEST}: size mismatch for {rel!r}. "
            f"Expected {expected_size}, got {size!r}."
        )


def test_upload_plan_exists_and_is_valid_json(sync_run):
    assert os.path.isfile(UPLOAD_PLAN), (
        f"Expected {UPLOAD_PLAN} to be created by sync.py."
    )
    with open(UPLOAD_PLAN, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, dict), (
        f"{UPLOAD_PLAN} must contain a JSON object. Got: {type(data).__name__}"
    )


def test_upload_plan_contents(sync_run):
    with open(UPLOAD_PLAN, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data.get("to_upload") == ["changelog.txt", "glossary.txt"], (
        f"upload_plan.json 'to_upload' must equal ['changelog.txt', 'glossary.txt']. "
        f"Got: {data.get('to_upload')!r}"
    )
    assert data.get("to_delete") == ["removed_doc.txt"], (
        f"upload_plan.json 'to_delete' must equal ['removed_doc.txt']. "
        f"Got: {data.get('to_delete')!r}"
    )
    assert data.get("unchanged") == ["intro.txt"], (
        f"upload_plan.json 'unchanged' must equal ['intro.txt']. "
        f"Got: {data.get('unchanged')!r}"
    )
    assert data.get("added") == ["changelog.txt"], (
        f"upload_plan.json 'added' must equal ['changelog.txt']. "
        f"Got: {data.get('added')!r}"
    )
    assert data.get("modified") == ["glossary.txt"], (
        f"upload_plan.json 'modified' must equal ['glossary.txt']. "
        f"Got: {data.get('modified')!r}"
    )


def test_upload_plan_summary(sync_run):
    with open(UPLOAD_PLAN, "r", encoding="utf-8") as f:
        data = json.load(f)
    expected_summary = {
        "added": 1,
        "modified": 1,
        "removed": 1,
        "unchanged": 1,
        "total_current": 3,
        "total_prior": 3,
    }
    assert data.get("summary") == expected_summary, (
        f"upload_plan.json 'summary' must equal {expected_summary}. "
        f"Got: {data.get('summary')!r}"
    )


def test_upload_plan_lists_are_sorted(sync_run):
    with open(UPLOAD_PLAN, "r", encoding="utf-8") as f:
        data = json.load(f)
    for key in ("to_upload", "to_delete", "unchanged", "added", "modified"):
        lst = data.get(key, [])
        assert lst == sorted(lst), (
            f"upload_plan.json '{key}' must be sorted ascending. Got: {lst!r}"
        )
