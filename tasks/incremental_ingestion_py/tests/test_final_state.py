import os
import re
import subprocess

import pytest

PROJECT_DIR = "/home/user/myproject"
SCRIPT_PATH = os.path.join(PROJECT_DIR, "incremental_ingest.py")
DOCS_INITIAL_DIR = os.path.join(PROJECT_DIR, "docs_initial")
DOCS_NEW_DIR = os.path.join(PROJECT_DIR, "docs_new")
OUTPUT_MD = os.path.join(PROJECT_DIR, "output.md")
OUTPUT_LOG = os.path.join(PROJECT_DIR, "output.log")
TRIAL_ID_PATH = "/logs/artifacts/trial_id"
BASE_INDEX_NAME = "harbor-inc-idx"
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
    assert os.path.isdir(DOCS_INITIAL_DIR), (
        f"Required docs_initial directory {DOCS_INITIAL_DIR} is missing."
    )
    assert os.path.isdir(DOCS_NEW_DIR), (
        f"Required docs_new directory {DOCS_NEW_DIR} is missing."
    )

    for path in (OUTPUT_MD, OUTPUT_LOG):
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


def test_script_exit_code_is_zero(run_agent_script):
    """The agent's incremental_ingest.py must run to completion with exit code 0."""
    completed = run_agent_script
    assert completed.returncode == 0, (
        f"incremental_ingest.py exited with non-zero status {completed.returncode}.\n"
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


def test_output_markdown_contains_required_headings_in_order():
    """The markdown output must contain the required headings in the right order."""
    with open(OUTPUT_MD, "r", encoding="utf-8") as f:
        content = f.read()
    top_heading = re.search(
        r"^\s*#\s+LlamaCloud Incremental Ingestion Result\s*$",
        content,
        re.MULTILINE,
    )
    assert top_heading, (
        f"Expected {OUTPUT_MD} to contain a top-level heading line "
        f"`# LlamaCloud Incremental Ingestion Result`, but none was found.\n"
        f"First 500 chars of output.md:\n{content[:500]!r}"
    )
    aurora_heading = re.search(
        r"^\s*##\s+Aurora Query Top Node\s*$",
        content,
        re.MULTILINE,
    )
    assert aurora_heading, (
        f"Expected {OUTPUT_MD} to contain a sub-heading line `## Aurora Query Top Node`, "
        f"but none was found.\nFirst 500 chars of output.md:\n{content[:500]!r}"
    )
    borealis_heading = re.search(
        r"^\s*##\s+Borealis Query Top Node\s*$",
        content,
        re.MULTILINE,
    )
    assert borealis_heading, (
        f"Expected {OUTPUT_MD} to contain a sub-heading line `## Borealis Query Top Node`, "
        f"but none was found.\nFirst 500 chars of output.md:\n{content[:500]!r}"
    )
    assert top_heading.start() < aurora_heading.start() < borealis_heading.start(), (
        "Expected headings to appear in order: `# LlamaCloud Incremental Ingestion "
        "Result`, then `## Aurora Query Top Node`, then `## Borealis Query Top Node`."
    )


def test_output_markdown_aurora_section_contains_expected_phrases():
    """The Aurora top-node section must include the expected Project Aurora phrases."""
    with open(OUTPUT_MD, "r", encoding="utf-8") as f:
        content = f.read()
    aurora_match = re.search(
        r"^\s*##\s+Aurora Query Top Node\s*$",
        content,
        re.MULTILINE,
    )
    borealis_match = re.search(
        r"^\s*##\s+Borealis Query Top Node\s*$",
        content,
        re.MULTILINE,
    )
    assert aurora_match and borealis_match, (
        "Required Aurora/Borealis sub-headings are missing from output.md."
    )
    aurora_section = content[aurora_match.end():borealis_match.start()].lower()
    assert "project aurora" in aurora_section, (
        f"Expected the `## Aurora Query Top Node` section of {OUTPUT_MD} to contain "
        "'Project Aurora' (case-insensitive), but it was not found.\n"
        f"Section content:\n{aurora_section[:1000]!r}"
    )
    assert "catalog every star in the milky way" in aurora_section, (
        f"Expected the `## Aurora Query Top Node` section of {OUTPUT_MD} to contain "
        "'catalog every star in the Milky Way' (case-insensitive), but it was not found.\n"
        f"Section content:\n{aurora_section[:1000]!r}"
    )


def test_output_markdown_borealis_section_contains_expected_phrases():
    """The Borealis top-node section must include the expected Project Borealis phrases."""
    with open(OUTPUT_MD, "r", encoding="utf-8") as f:
        content = f.read()
    borealis_match = re.search(
        r"^\s*##\s+Borealis Query Top Node\s*$",
        content,
        re.MULTILINE,
    )
    assert borealis_match, (
        "Required `## Borealis Query Top Node` sub-heading is missing from output.md."
    )
    borealis_section = content[borealis_match.end():].lower()
    assert "project borealis" in borealis_section, (
        f"Expected the `## Borealis Query Top Node` section of {OUTPUT_MD} to contain "
        "'Project Borealis' (case-insensitive), but it was not found.\n"
        f"Section content:\n{borealis_section[:1000]!r}"
    )
    assert "map every ocean current on earth" in borealis_section, (
        f"Expected the `## Borealis Query Top Node` section of {OUTPUT_MD} to contain "
        "'map every ocean current on Earth' (case-insensitive), but it was not found.\n"
        f"Section content:\n{borealis_section[:1000]!r}"
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
    """The log file must contain an `index_name: harbor-inc-idx-<trial_id>` line."""
    expected = _expected_index_name()
    with open(OUTPUT_LOG, "r", encoding="utf-8") as f:
        log_content = f.read()
    pattern = re.compile(
        r"^\s*index_name\s*:\s*" + re.escape(expected) + r"\s*$",
        re.MULTILINE,
    )
    assert pattern.search(log_content), (
        f"Expected {OUTPUT_LOG} to contain a line `index_name: {expected}`, "
        f"but no such line was found.\nLog content:\n{log_content!r}"
    )


def test_output_log_contains_num_initial_files_line():
    """The log file must contain a `num_initial_files: <N>` line with N >= 1."""
    with open(OUTPUT_LOG, "r", encoding="utf-8") as f:
        log_content = f.read()
    match = re.search(
        r"^\s*num_initial_files\s*:\s*(\d+)\s*$",
        log_content,
        re.MULTILINE,
    )
    assert match, (
        f"Expected {OUTPUT_LOG} to contain a line matching `num_initial_files: <N>`, "
        f"but no such line was found.\nLog content:\n{log_content!r}"
    )
    num = int(match.group(1))
    assert num >= 1, f"Expected num_initial_files to be at least 1, got {num}."


def test_output_log_contains_num_new_files_uploaded_line():
    """The log file must contain a `num_new_files_uploaded: <N>` line with N >= 1."""
    with open(OUTPUT_LOG, "r", encoding="utf-8") as f:
        log_content = f.read()
    match = re.search(
        r"^\s*num_new_files_uploaded\s*:\s*(\d+)\s*$",
        log_content,
        re.MULTILINE,
    )
    assert match, (
        f"Expected {OUTPUT_LOG} to contain a line matching `num_new_files_uploaded: <N>`, "
        f"but no such line was found.\nLog content:\n{log_content!r}"
    )
    num = int(match.group(1))
    assert num >= 1, f"Expected num_new_files_uploaded to be at least 1, got {num}."


def test_output_log_contains_aurora_num_retrieved_line():
    """The log file must contain an `aurora_num_retrieved: <N>` line with N >= 1."""
    with open(OUTPUT_LOG, "r", encoding="utf-8") as f:
        log_content = f.read()
    match = re.search(
        r"^\s*aurora_num_retrieved\s*:\s*(\d+)\s*$",
        log_content,
        re.MULTILINE,
    )
    assert match, (
        f"Expected {OUTPUT_LOG} to contain a line matching `aurora_num_retrieved: <N>`, "
        f"but no such line was found.\nLog content:\n{log_content!r}"
    )
    num = int(match.group(1))
    assert num >= 1, f"Expected aurora_num_retrieved to be at least 1, got {num}."


def test_output_log_contains_borealis_num_retrieved_line():
    """The log file must contain a `borealis_num_retrieved: <N>` line with N >= 1."""
    with open(OUTPUT_LOG, "r", encoding="utf-8") as f:
        log_content = f.read()
    match = re.search(
        r"^\s*borealis_num_retrieved\s*:\s*(\d+)\s*$",
        log_content,
        re.MULTILINE,
    )
    assert match, (
        f"Expected {OUTPUT_LOG} to contain a line matching `borealis_num_retrieved: <N>`, "
        f"but no such line was found.\nLog content:\n{log_content!r}"
    )
    num = int(match.group(1))
    assert num >= 1, f"Expected borealis_num_retrieved to be at least 1, got {num}."


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


def test_borealis_content_retrievable_from_managed_index():
    """The incrementally-uploaded Borealis file must be retrievable via the managed index."""
    api_key = os.environ.get("LLAMA_CLOUD_API_KEY")
    assert api_key, (
        "Verifier environment must have LLAMA_CLOUD_API_KEY set to query the "
        "managed index for Borealis content."
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
            f"Could not connect to managed LlamaCloud index `{expected}` for "
            f"Borealis retrieval verification: {type(exc).__name__}: {exc}"
        )

    try:
        nodes = index.as_retriever().retrieve(
            "What is the mission of Project Borealis?"
        )
    except Exception as exc:  # noqa: BLE001
        pytest.fail(
            f"Retrieval against managed LlamaCloud index `{expected}` failed: "
            f"{type(exc).__name__}: {exc}"
        )

    assert nodes, (
        f"Retrieval for the Borealis query returned zero nodes from managed "
        f"index `{expected}`; expected the incrementally uploaded Borealis "
        f"document to be retrievable."
    )

    combined_text = "\n".join(
        getattr(n.node, "text", None) or n.node.get_content() for n in nodes
    ).lower()
    assert "project borealis" in combined_text, (
        f"Expected at least one retrieved node from managed index `{expected}` "
        f"to mention 'Project Borealis' (case-insensitive). Retrieved text "
        f"(truncated): {combined_text[:1000]!r}"
    )
    assert "map every ocean current on earth" in combined_text, (
        f"Expected at least one retrieved node from managed index `{expected}` "
        f"to contain 'map every ocean current on Earth' (case-insensitive). "
        f"This is the phrase from the incrementally-uploaded `docs_new/project_borealis.txt`. "
        f"Retrieved text (truncated): {combined_text[:1000]!r}"
    )
