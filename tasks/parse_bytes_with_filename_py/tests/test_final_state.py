import json
import os
import re
import subprocess

import pytest

PROJECT_DIR = "/home/user/parse_bytes_task"
DOCS_DIR = os.path.join(PROJECT_DIR, "docs")
OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")
SCRIPT_PATH = os.path.join(PROJECT_DIR, "parse_bytes.py")
MANIFEST_PATH = os.path.join(OUTPUT_DIR, "manifest.json")

EXPECTED_ENTRIES = [
    {
        "file_name": "alpha_report.pdf",
        "output": "output/alpha_report.md",
        "headline": "Alpha Status Report",
    },
    {
        "file_name": "beta_invoice.pdf",
        "output": "output/beta_invoice.md",
        "headline": "Beta Invoice 0001",
    },
    {
        "file_name": "gamma_memo.pdf",
        "output": "output/gamma_memo.md",
        "headline": "Gamma Internal Memo",
    },
]


@pytest.fixture(scope="module")
def script_ran():
    """Run parse_bytes.py once after wiping the output directory."""
    assert os.path.isfile(SCRIPT_PATH), (
        f"Expected the executor-created script at {SCRIPT_PATH}, but it is missing."
    )

    # Wipe any pre-existing output so we only verify freshly produced artifacts.
    if os.path.isdir(OUTPUT_DIR):
        for root, dirs, files in os.walk(OUTPUT_DIR, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(OUTPUT_DIR)

    env = os.environ.copy()
    result = subprocess.run(
        ["python3", "parse_bytes.py"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        env=env,
        timeout=900,
    )
    assert result.returncode == 0, (
        "parse_bytes.py did not exit with status 0.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    return result


def test_script_uses_required_api_patterns():
    """The script must use llama_cloud_services.LlamaParse and the bytes/file_name pattern."""
    assert os.path.isfile(SCRIPT_PATH), f"Missing script {SCRIPT_PATH}."
    with open(SCRIPT_PATH, "r", encoding="utf-8", errors="ignore") as fp:
        source = fp.read()

    assert "from llama_cloud_services" in source, (
        "parse_bytes.py must import from 'llama_cloud_services' "
        "(e.g. 'from llama_cloud_services import LlamaParse')."
    )
    assert re.search(r"\bLlamaParse\b", source), (
        "parse_bytes.py must reference the 'LlamaParse' class."
    )
    assert re.search(r"\bload_data\b", source), (
        "parse_bytes.py must call 'load_data' on the LlamaParse client."
    )
    assert "extra_info" in source, (
        "parse_bytes.py must pass 'extra_info' to load_data."
    )
    assert "file_name" in source, (
        "parse_bytes.py must include the 'file_name' key in extra_info "
        "(required when passing bytes to LlamaParse)."
    )


def test_output_directory_exists(script_ran):
    assert os.path.isdir(OUTPUT_DIR), (
        f"Expected output directory {OUTPUT_DIR} to exist after running parse_bytes.py."
    )


@pytest.mark.parametrize("entry", EXPECTED_ENTRIES, ids=[e["file_name"] for e in EXPECTED_ENTRIES])
def test_markdown_output_exists_and_contains_headline(script_ran, entry):
    md_path = os.path.join(PROJECT_DIR, entry["output"])
    assert os.path.isfile(md_path), (
        f"Expected markdown output file {md_path} for {entry['file_name']}, but it is missing."
    )
    assert os.path.getsize(md_path) > 0, (
        f"Expected markdown output {md_path} to be non-empty."
    )
    with open(md_path, "rb") as fp:
        raw = fp.read()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        pytest.fail(f"Markdown file {md_path} is not valid UTF-8: {exc}")

    headline = entry["headline"].lower()
    assert headline in text.lower(), (
        f"Expected markdown for {entry['file_name']} to contain the headline "
        f"'{entry['headline']}' (case-insensitive). First 500 chars: {text[:500]!r}"
    )


def test_manifest_exists_and_is_valid_json(script_ran):
    assert os.path.isfile(MANIFEST_PATH), (
        f"Expected manifest JSON at {MANIFEST_PATH}, but it is missing."
    )
    with open(MANIFEST_PATH, "r", encoding="utf-8") as fp:
        try:
            data = json.load(fp)
        except json.JSONDecodeError as exc:
            pytest.fail(f"Manifest at {MANIFEST_PATH} is not valid JSON: {exc}")
    assert isinstance(data, dict), (
        f"Top-level value in {MANIFEST_PATH} must be a JSON object, got {type(data).__name__}."
    )
    assert "parsed" in data, (
        f"Manifest at {MANIFEST_PATH} must contain a 'parsed' key."
    )
    assert isinstance(data["parsed"], list), (
        f"Manifest 'parsed' field must be a JSON list, got {type(data['parsed']).__name__}."
    )
    assert len(data["parsed"]) == len(EXPECTED_ENTRIES), (
        f"Expected 'parsed' to contain {len(EXPECTED_ENTRIES)} entries (one per PDF), "
        f"got {len(data['parsed'])}."
    )


def test_manifest_entries_have_correct_shape_and_order(script_ran):
    with open(MANIFEST_PATH, "r", encoding="utf-8") as fp:
        data = json.load(fp)
    entries = data["parsed"]

    expected_names = [e["file_name"] for e in EXPECTED_ENTRIES]
    actual_names = [entry.get("file_name") for entry in entries]
    assert actual_names == expected_names, (
        f"Expected 'parsed' entries to be sorted by file_name in the order "
        f"{expected_names}, got {actual_names}."
    )

    for entry, expected in zip(entries, EXPECTED_ENTRIES):
        assert isinstance(entry, dict), (
            f"Each manifest entry must be a JSON object, got {type(entry).__name__}."
        )
        assert set(entry.keys()) >= {"file_name", "output", "chars"}, (
            f"Manifest entry {entry} must contain keys 'file_name', 'output', and 'chars'."
        )
        assert entry["output"] == expected["output"], (
            f"Manifest entry for {expected['file_name']}: expected 'output' "
            f"{expected['output']!r}, got {entry['output']!r}."
        )
        assert isinstance(entry["chars"], int), (
            f"Manifest entry for {expected['file_name']}: 'chars' must be an integer, "
            f"got {type(entry['chars']).__name__}."
        )
        assert entry["chars"] > 0, (
            f"Manifest entry for {expected['file_name']}: 'chars' must be a positive integer, "
            f"got {entry['chars']}."
        )


def test_manifest_char_counts_match_files(script_ran):
    with open(MANIFEST_PATH, "r", encoding="utf-8") as fp:
        data = json.load(fp)
    for entry in data["parsed"]:
        out_path = os.path.join(PROJECT_DIR, entry["output"])
        assert os.path.isfile(out_path), (
            f"Manifest references missing output file: {out_path}."
        )
        with open(out_path, "r", encoding="utf-8") as md_fp:
            actual_chars = len(md_fp.read())
        assert entry["chars"] == actual_chars, (
            f"Manifest entry for {entry['file_name']}: expected 'chars' to equal the "
            f"character count of {out_path} ({actual_chars}), got {entry['chars']}."
        )
