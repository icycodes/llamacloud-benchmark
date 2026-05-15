import os
import re
import subprocess

import pytest

PROJECT_DIR = "/home/user/myproject"
SCRIPT_PATH = os.path.join(PROJECT_DIR, "build_and_retrieve.py")
DOCS_DIR = os.path.join(PROJECT_DIR, "docs")
OUTPUT_MD = os.path.join(PROJECT_DIR, "output.md")
OUTPUT_LOG = os.path.join(PROJECT_DIR, "output.log")
TRIAL_ID_PATH = "/logs/artifacts/trial_id"
BASE_INDEX_NAME = "harbor-mgr-idx"
PROJECT_NAME = "Default"


def _read_trial_id() -> str:
    with open(TRIAL_ID_PATH, "r", encoding="utf-8") as f:
        return f.read().strip()


def _expected_index_name() -> str:
    return f"{BASE_INDEX_NAME}-{_read_trial_id()}"


@pytest.fixture(scope="session", autouse=True)
def run_agent_script():
    """Clean previously generated outputs and execute the agent's script once."""
    assert os.path.isfile(SCRIPT_PATH), (
        f"Agent's script {SCRIPT_PATH} does not exist. The agent must create it."
    )
    assert os.path.isdir(DOCS_DIR), (
        f"Required docs directory {DOCS_DIR} is missing."
    )

    for path in (OUTPUT_MD, OUTPUT_LOG):
        if os.path.isfile(path):
            os.remove(path)

    completed = subprocess.run(
        ["python3", SCRIPT_PATH],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=600,
    )
    yield completed


def test_script_exit_code_is_zero(run_agent_script):
    """The agent's build_and_retrieve.py must run to completion with exit code 0."""
    completed = run_agent_script
    assert completed.returncode == 0, (
        f"build_and_retrieve.py exited with non-zero status {completed.returncode}.\n"
        f"STDOUT:\n{completed.stdout}\n"
        f"STDERR:\n{completed.stderr}"
    )


def test_output_markdown_file_exists():
    """The retrieval markdown output file must exist and be non-empty."""
    assert os.path.isfile(OUTPUT_MD), (
        f"Expected markdown output file at {OUTPUT_MD} to be created by the script."
    )
    assert os.path.getsize(OUTPUT_MD) > 0, (
        f"Markdown output file {OUTPUT_MD} exists but is empty."
    )


def test_output_markdown_contains_required_headings():
    """The markdown output must contain the required top heading and sub-heading."""
    with open(OUTPUT_MD, "r", encoding="utf-8") as f:
        content = f.read()
    top_heading = re.search(
        r"^\s*#\s+LlamaCloud Retrieval Result\s*$",
        content,
        re.MULTILINE,
    )
    assert top_heading, (
        f"Expected {OUTPUT_MD} to contain a top-level heading line "
        f"`# LlamaCloud Retrieval Result`, but none was found.\n"
        f"First 500 chars of output.md:\n{content[:500]!r}"
    )
    sub_heading = re.search(
        r"^\s*##\s+Top Node\s*$",
        content,
        re.MULTILINE,
    )
    assert sub_heading, (
        f"Expected {OUTPUT_MD} to contain a sub-heading line `## Top Node`, "
        f"but none was found.\n"
        f"First 500 chars of output.md:\n{content[:500]!r}"
    )
    assert top_heading.start() < sub_heading.start(), (
        "Expected the `# LlamaCloud Retrieval Result` heading to appear before "
        "the `## Top Node` sub-heading."
    )


def test_output_markdown_contains_expected_top_node_phrases():
    """The retrieved top node must include the expected Project Aurora phrases."""
    with open(OUTPUT_MD, "r", encoding="utf-8") as f:
        content = f.read().lower()
    assert "project aurora" in content, (
        f"Expected the parsed markdown at {OUTPUT_MD} to contain the phrase "
        "'Project Aurora' (case-insensitive), but it was not found."
    )
    assert "catalog every star in the milky way" in content, (
        f"Expected the parsed markdown at {OUTPUT_MD} to contain the phrase "
        "'catalog every star in the Milky Way' (case-insensitive), but it was "
        "not found."
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
    """The log file must contain a `trial_id: <value>` line matching the harness value."""
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


def test_output_log_contains_index_name_line():
    """The log file must contain an `index_name: harbor-mgr-idx-<trial_id>` line."""
    expected = _expected_index_name()
    with open(OUTPUT_LOG, "r", encoding="utf-8") as f:
        log_content = f.read()
    pattern = re.compile(
        r"^\s*index_name\s*:\s*" + re.escape(expected) + r"\s*$",
        re.MULTILINE,
    )
    assert pattern.search(log_content), (
        f"Expected {OUTPUT_LOG} to contain a line `index_name: {expected}`, "
        f"but no such line was found.\n"
        f"Log content:\n{log_content!r}"
    )


def test_output_log_contains_num_retrieved_line():
    """The log file must contain a `num_retrieved: <N>` line with N >= 1."""
    with open(OUTPUT_LOG, "r", encoding="utf-8") as f:
        log_content = f.read()
    match = re.search(
        r"^\s*num_retrieved\s*:\s*(\d+)\s*$",
        log_content,
        re.MULTILINE,
    )
    assert match, (
        f"Expected {OUTPUT_LOG} to contain a line matching `num_retrieved: <N>` "
        f"with N a non-negative integer, but no such line was found.\n"
        f"Log content:\n{log_content!r}"
    )
    num = int(match.group(1))
    assert num >= 1, f"Expected num_retrieved to be at least 1, got {num}."


def test_managed_index_exists_on_llamacloud():
    """The managed index must actually exist on the LlamaCloud service."""
    api_key = os.environ.get("LLAMA_CLOUD_API_KEY")
    assert api_key, (
        "Verifier environment must have LLAMA_CLOUD_API_KEY set to confirm the "
        "managed index exists on LlamaCloud."
    )
    try:
        from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
    except ImportError as exc:
        pytest.fail(
            "Verifier could not import "
            "`llama_index.indices.managed.llama_cloud.LlamaCloudIndex`: "
            f"{exc}"
        )

    expected = _expected_index_name()
    try:
        index = LlamaCloudIndex(
            name=expected,
            project_name=PROJECT_NAME,
            api_key=api_key,
        )
    except Exception as exc:  # noqa: BLE001
        pytest.fail(
            f"Expected a managed LlamaCloud index named `{expected}` to exist "
            f"in project `{PROJECT_NAME}` after the script ran, but connecting "
            f"to it raised: {type(exc).__name__}: {exc}"
        )
    assert index is not None, (
        f"LlamaCloudIndex constructor returned None for index `{expected}`."
    )
