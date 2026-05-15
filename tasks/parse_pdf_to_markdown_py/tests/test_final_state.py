import os
import re
import subprocess

import pytest

PROJECT_DIR = "/home/user/myproject"
SCRIPT_PATH = os.path.join(PROJECT_DIR, "parse.py")
SAMPLE_PDF = os.path.join(PROJECT_DIR, "sample.pdf")
OUTPUT_MD = os.path.join(PROJECT_DIR, "sample.md")
MISSING_PDF = os.path.join(PROJECT_DIR, "does_not_exist.pdf")


@pytest.fixture(scope="module")
def run_parse_script():
    # Pre-cleanup: remove the markdown output if a previous run left it behind.
    if os.path.exists(OUTPUT_MD):
        os.remove(OUTPUT_MD)

    env = os.environ.copy()
    result = subprocess.run(
        ["python3", SCRIPT_PATH, "--input", SAMPLE_PDF, "--output", OUTPUT_MD],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
        env=env,
        timeout=300,
    )
    return result


def test_parse_script_exists():
    assert os.path.isfile(SCRIPT_PATH), \
        f"Expected the parse.py CLI script at {SCRIPT_PATH}, but it does not exist."


def test_parse_script_uses_llama_cloud_sdk():
    with open(SCRIPT_PATH, "r", encoding="utf-8") as fh:
        contents = fh.read()
    assert re.search(r"from\s+llama_cloud\s+import\s+LlamaCloud", contents), \
        ("parse.py must import `LlamaCloud` from the `llama_cloud` package "
         "(e.g., `from llama_cloud import LlamaCloud`).")


def test_parse_script_uses_cost_effective_tier():
    with open(SCRIPT_PATH, "r", encoding="utf-8") as fh:
        contents = fh.read()
    assert "cost_effective" in contents, \
        "parse.py must pass tier=\"cost_effective\" to client.parsing.parse."


def test_parse_script_uses_latest_version():
    with open(SCRIPT_PATH, "r", encoding="utf-8") as fh:
        contents = fh.read()
    assert re.search(r"version\s*=\s*[\"']latest[\"']", contents), \
        "parse.py must pass version=\"latest\" to client.parsing.parse."


def test_parse_script_requests_markdown_expand():
    with open(SCRIPT_PATH, "r", encoding="utf-8") as fh:
        contents = fh.read()
    assert re.search(r"expand\s*=\s*\[[^\]]*[\"']markdown[\"']", contents), \
        "parse.py must request `markdown` via the `expand` parameter on client.parsing.parse."


def test_parse_script_runs_successfully(run_parse_script):
    result = run_parse_script
    assert result.returncode == 0, \
        (f"parse.py exited with non-zero status {result.returncode}.\n"
         f"stdout: {result.stdout}\nstderr: {result.stderr}")


def test_stdout_reports_one_page(run_parse_script):
    result = run_parse_script
    # The sample PDF has exactly one page.
    lines = [ln.strip() for ln in result.stdout.splitlines() if ln.strip()]
    assert "Parsed 1 pages" in lines, \
        (f"Expected stdout to include the line 'Parsed 1 pages' (the sample PDF has 1 page); "
         f"actual stdout was: {result.stdout!r}")


def test_output_markdown_file_created(run_parse_script):
    assert os.path.isfile(OUTPUT_MD), \
        f"Expected output markdown file at {OUTPUT_MD}, but it was not created."


def test_output_markdown_file_nonempty(run_parse_script):
    size = os.path.getsize(OUTPUT_MD)
    assert size > 0, f"Output markdown file {OUTPUT_MD} is empty (size={size})."


def test_output_markdown_contains_hello_llamaparse(run_parse_script):
    with open(OUTPUT_MD, "r", encoding="utf-8") as fh:
        contents = fh.read()
    assert "hello llamaparse" in contents.lower(), \
        (f"Expected the parsed markdown to contain 'Hello LlamaParse' (case-insensitive); "
         f"got content (first 500 chars): {contents[:500]!r}")


def test_output_markdown_contains_harbor_test_document(run_parse_script):
    with open(OUTPUT_MD, "r", encoding="utf-8") as fh:
        contents = fh.read()
    assert "harbor test document" in contents.lower(), \
        (f"Expected the parsed markdown to contain 'Harbor Test Document' (case-insensitive); "
         f"got content (first 500 chars): {contents[:500]!r}")


def test_script_fails_on_missing_input():
    # Ensure the missing path truly does not exist.
    if os.path.exists(MISSING_PDF):
        os.remove(MISSING_PDF)
    env = os.environ.copy()
    result = subprocess.run(
        ["python3", SCRIPT_PATH, "--input", MISSING_PDF, "--output", "/tmp/should_not_be_created.md"],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
        env=env,
        timeout=120,
    )
    assert result.returncode != 0, \
        (f"parse.py must exit with a non-zero status when --input refers to a missing file; "
         f"got returncode=0 with stdout: {result.stdout!r}, stderr: {result.stderr!r}")
