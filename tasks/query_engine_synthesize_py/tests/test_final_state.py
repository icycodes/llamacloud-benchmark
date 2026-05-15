import os
import re
import subprocess

import pytest

PROJECT_DIR = "/home/user/myproject"
SCRIPT_PATH = os.path.join(PROJECT_DIR, "run_query_engine.py")
DOCS_DIR = os.path.join(PROJECT_DIR, "docs")
OUTPUT_MD = os.path.join(PROJECT_DIR, "output.md")
OUTPUT_LOG = os.path.join(PROJECT_DIR, "output.log")
TRIAL_ID_PATH = "/logs/artifacts/trial_id"
BASE_INDEX_NAME = "harbor-qe-idx"
PROJECT_NAME = "Default"
EXPECTED_QUESTION = "What is the mission of Project Aurora?"


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
    """The agent's run_query_engine.py must run to completion with exit code 0."""
    completed = run_agent_script
    assert completed.returncode == 0, (
        f"run_query_engine.py exited with non-zero status {completed.returncode}.\n"
        f"STDOUT:\n{completed.stdout}\n"
        f"STDERR:\n{completed.stderr}"
    )


def test_output_markdown_file_exists():
    """The query engine markdown output file must exist and be non-empty."""
    assert os.path.isfile(OUTPUT_MD), (
        f"Expected markdown output file at {OUTPUT_MD} to be created by the script."
    )
    assert os.path.getsize(OUTPUT_MD) > 0, (
        f"Markdown output file {OUTPUT_MD} exists but is empty."
    )


def _find_heading(content: str, pattern: str):
    return re.search(pattern, content, re.MULTILINE)


def test_output_markdown_headings_present_and_ordered():
    """The markdown output must contain the required headings in the right order."""
    with open(OUTPUT_MD, "r", encoding="utf-8") as f:
        content = f.read()
    top = _find_heading(content, r"^\s*#\s+LlamaCloud Query Engine Result\s*$")
    question = _find_heading(content, r"^\s*##\s+Question\s*$")
    answer = _find_heading(content, r"^\s*##\s+Answer\s*$")
    sources = _find_heading(content, r"^\s*##\s+Source Nodes\s*$")
    assert top, (
        f"Expected {OUTPUT_MD} to contain a top-level heading "
        f"`# LlamaCloud Query Engine Result`, but none was found.\n"
        f"First 500 chars of output.md:\n{content[:500]!r}"
    )
    assert question, (
        f"Expected {OUTPUT_MD} to contain a `## Question` sub-heading, but none "
        f"was found."
    )
    assert answer, (
        f"Expected {OUTPUT_MD} to contain a `## Answer` sub-heading, but none "
        f"was found."
    )
    assert sources, (
        f"Expected {OUTPUT_MD} to contain a `## Source Nodes` sub-heading, but "
        f"none was found."
    )
    assert top.start() < question.start() < answer.start() < sources.start(), (
        "Expected the markdown headings to appear in this order: "
        "`# LlamaCloud Query Engine Result`, `## Question`, `## Answer`, "
        "`## Source Nodes`."
    )


def test_output_markdown_question_text():
    """The question section must include the exact question text."""
    with open(OUTPUT_MD, "r", encoding="utf-8") as f:
        content = f.read()
    question_match = _find_heading(content, r"^\s*##\s+Question\s*$")
    answer_match = _find_heading(content, r"^\s*##\s+Answer\s*$")
    assert question_match and answer_match, (
        "Markdown is missing `## Question` and/or `## Answer` headings; cannot "
        "extract the question text section."
    )
    question_section = content[question_match.end():answer_match.start()]
    assert EXPECTED_QUESTION in question_section, (
        f"Expected the section under `## Question` to contain the exact text "
        f"`{EXPECTED_QUESTION}`, but it was not found.\n"
        f"Question section content:\n{question_section!r}"
    )


def test_output_markdown_answer_is_non_empty():
    """The answer section must contain at least one non-whitespace character."""
    with open(OUTPUT_MD, "r", encoding="utf-8") as f:
        content = f.read()
    answer_match = _find_heading(content, r"^\s*##\s+Answer\s*$")
    sources_match = _find_heading(content, r"^\s*##\s+Source Nodes\s*$")
    assert answer_match and sources_match, (
        "Markdown is missing `## Answer` and/or `## Source Nodes` headings; "
        "cannot extract the answer section."
    )
    answer_section = content[answer_match.end():sources_match.start()]
    assert answer_section.strip(), (
        f"Expected the section under `## Answer` (before `## Source Nodes`) to "
        f"contain a non-empty synthesized answer, but it appears empty.\n"
        f"Answer section content:\n{answer_section!r}"
    )


def test_output_markdown_source_nodes_section_has_expected_phrases():
    """The source-nodes section must include the Project Aurora retrieval evidence."""
    with open(OUTPUT_MD, "r", encoding="utf-8") as f:
        content = f.read()
    sources_match = _find_heading(content, r"^\s*##\s+Source Nodes\s*$")
    assert sources_match, "Markdown is missing the `## Source Nodes` heading."
    sources_section = content[sources_match.end():].lower()
    assert "project aurora" in sources_section, (
        f"Expected the `## Source Nodes` section in {OUTPUT_MD} to mention "
        f"'Project Aurora' (case-insensitive), but it was not found."
    )
    assert "catalog every star in the milky way" in sources_section, (
        f"Expected the `## Source Nodes` section in {OUTPUT_MD} to contain the "
        f"phrase 'catalog every star in the Milky Way' (case-insensitive), but "
        f"it was not found."
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
    """The log file must contain an `index_name: harbor-qe-idx-<trial_id>` line."""
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


def test_output_log_contains_llm_model_line():
    """The log file must contain an `llm_model: gpt-4o-mini` line."""
    with open(OUTPUT_LOG, "r", encoding="utf-8") as f:
        log_content = f.read()
    pattern = re.compile(
        r"^\s*llm_model\s*:\s*gpt-4o-mini\s*$",
        re.MULTILINE,
    )
    assert pattern.search(log_content), (
        f"Expected {OUTPUT_LOG} to contain a line `llm_model: gpt-4o-mini`, "
        f"but no such line was found.\n"
        f"Log content:\n{log_content!r}"
    )


def test_output_log_contains_num_source_nodes_line():
    """The log file must contain a `num_source_nodes: <N>` line with N >= 1."""
    with open(OUTPUT_LOG, "r", encoding="utf-8") as f:
        log_content = f.read()
    match = re.search(
        r"^\s*num_source_nodes\s*:\s*(\d+)\s*$",
        log_content,
        re.MULTILINE,
    )
    assert match, (
        f"Expected {OUTPUT_LOG} to contain a line matching `num_source_nodes: "
        f"<N>` with N a non-negative integer, but no such line was found.\n"
        f"Log content:\n{log_content!r}"
    )
    num = int(match.group(1))
    assert num >= 1, f"Expected num_source_nodes to be at least 1, got {num}."


def test_output_log_contains_answer_length_line():
    """The log file must contain an `answer_length: <L>` line with L >= 1."""
    with open(OUTPUT_LOG, "r", encoding="utf-8") as f:
        log_content = f.read()
    match = re.search(
        r"^\s*answer_length\s*:\s*(\d+)\s*$",
        log_content,
        re.MULTILINE,
    )
    assert match, (
        f"Expected {OUTPUT_LOG} to contain a line matching `answer_length: <L>` "
        f"with L a non-negative integer, but no such line was found.\n"
        f"Log content:\n{log_content!r}"
    )
    length = int(match.group(1))
    assert length >= 1, f"Expected answer_length to be at least 1, got {length}."


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
