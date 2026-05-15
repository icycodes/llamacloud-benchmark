import os
import re
import subprocess

import pytest

PROJECT_DIR = "/home/user/myproject"
SCRIPT_PATH = os.path.join(PROJECT_DIR, "build_composite.py")
DOCS_ASTRO = os.path.join(PROJECT_DIR, "docs_astronomy")
DOCS_COOK = os.path.join(PROJECT_DIR, "docs_cooking")
OUTPUT_MD = os.path.join(PROJECT_DIR, "output.md")
OUTPUT_LOG = os.path.join(PROJECT_DIR, "output.log")
TRIAL_ID_PATH = "/logs/artifacts/trial_id"
PROJECT_NAME = "Default"
BASE_ASTRO = "harbor-cmp-astro"
BASE_COOK = "harbor-cmp-cook"
BASE_RETRIEVER = "harbor-cmp-retriever"


def _read_trial_id() -> str:
    with open(TRIAL_ID_PATH, "r", encoding="utf-8") as f:
        return f.read().strip()


def _expected_astro_name() -> str:
    return f"{BASE_ASTRO}-{_read_trial_id()}"


def _expected_cook_name() -> str:
    return f"{BASE_COOK}-{_read_trial_id()}"


def _expected_retriever_name() -> str:
    return f"{BASE_RETRIEVER}-{_read_trial_id()}"


@pytest.fixture(scope="session", autouse=True)
def run_agent_script():
    """Clean previously generated outputs and execute the agent's script once."""
    assert os.path.isfile(SCRIPT_PATH), (
        f"Agent's script {SCRIPT_PATH} does not exist. The agent must create it."
    )
    assert os.path.isdir(DOCS_ASTRO), (
        f"Required docs directory {DOCS_ASTRO} is missing."
    )
    assert os.path.isdir(DOCS_COOK), (
        f"Required docs directory {DOCS_COOK} is missing."
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
    """The agent's build_composite.py must run to completion with exit code 0."""
    completed = run_agent_script
    assert completed.returncode == 0, (
        f"build_composite.py exited with non-zero status {completed.returncode}.\n"
        f"STDOUT:\n{completed.stdout}\n"
        f"STDERR:\n{completed.stderr}"
    )


def test_output_markdown_file_exists():
    """The composite retrieval markdown output file must exist and be non-empty."""
    assert os.path.isfile(OUTPUT_MD), (
        f"Expected markdown output file at {OUTPUT_MD} to be created by the script."
    )
    assert os.path.getsize(OUTPUT_MD) > 0, (
        f"Markdown output file {OUTPUT_MD} exists but is empty."
    )


def test_output_markdown_headings_present_and_ordered():
    """The markdown must contain the three required headings in the specified order."""
    with open(OUTPUT_MD, "r", encoding="utf-8") as f:
        content = f.read()
    top = re.search(
        r"^\s*#\s+LlamaCloud Composite Retrieval Result\s*$",
        content,
        re.MULTILINE,
    )
    assert top, (
        f"Expected {OUTPUT_MD} to contain a top-level heading line "
        f"`# LlamaCloud Composite Retrieval Result`, but none was found.\n"
        f"First 500 chars of output.md:\n{content[:500]!r}"
    )
    astro = re.search(
        r"^\s*##\s+Astronomy Query Top Node\s*$",
        content,
        re.MULTILINE,
    )
    assert astro, (
        f"Expected {OUTPUT_MD} to contain a sub-heading `## Astronomy Query Top Node`, "
        f"but none was found.\n"
        f"First 500 chars of output.md:\n{content[:500]!r}"
    )
    cook = re.search(
        r"^\s*##\s+Cooking Query Top Node\s*$",
        content,
        re.MULTILINE,
    )
    assert cook, (
        f"Expected {OUTPUT_MD} to contain a sub-heading `## Cooking Query Top Node`, "
        f"but none was found.\n"
        f"First 500 chars of output.md:\n{content[:500]!r}"
    )
    assert top.start() < astro.start() < cook.start(), (
        "Expected headings to appear in order: "
        "`# LlamaCloud Composite Retrieval Result`, then "
        "`## Astronomy Query Top Node`, then `## Cooking Query Top Node`."
    )


def test_astronomy_top_node_section_contains_expected_phrases():
    """The astronomy section must mention Project Aurora and its mission phrase."""
    with open(OUTPUT_MD, "r", encoding="utf-8") as f:
        content = f.read()
    astro = re.search(
        r"^\s*##\s+Astronomy Query Top Node\s*$",
        content,
        re.MULTILINE,
    )
    cook = re.search(
        r"^\s*##\s+Cooking Query Top Node\s*$",
        content,
        re.MULTILINE,
    )
    assert astro and cook, (
        "Astronomy and Cooking sub-headings must both exist before this check."
    )
    section = content[astro.end():cook.start()].lower()
    assert "project aurora" in section, (
        f"Expected the `## Astronomy Query Top Node` section of {OUTPUT_MD} to "
        f"contain the case-insensitive substring 'Project Aurora', but it did not.\n"
        f"Section content:\n{section!r}"
    )
    assert "catalog every star in the milky way" in section, (
        f"Expected the `## Astronomy Query Top Node` section of {OUTPUT_MD} to "
        f"contain the case-insensitive substring 'catalog every star in the Milky Way', "
        f"but it did not.\nSection content:\n{section!r}"
    )


def test_cooking_top_node_section_contains_expected_phrases():
    """The cooking section must mention both honey and lemon."""
    with open(OUTPUT_MD, "r", encoding="utf-8") as f:
        content = f.read()
    cook = re.search(
        r"^\s*##\s+Cooking Query Top Node\s*$",
        content,
        re.MULTILINE,
    )
    assert cook, "Cooking sub-heading must exist before this check."
    section = content[cook.end():].lower()
    assert "honey" in section, (
        f"Expected the `## Cooking Query Top Node` section of {OUTPUT_MD} to "
        f"contain the case-insensitive substring 'honey', but it did not.\n"
        f"Section content:\n{section!r}"
    )
    assert "lemon" in section, (
        f"Expected the `## Cooking Query Top Node` section of {OUTPUT_MD} to "
        f"contain the case-insensitive substring 'lemon', but it did not.\n"
        f"Section content:\n{section!r}"
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
        f"Expected {OUTPUT_LOG} to contain a line `trial_id: {trial_id}`, "
        f"but no such line was found.\n"
        f"Log content:\n{log_content!r}"
    )


def test_output_log_contains_astro_index_name_line():
    """The log file must contain an `astro_index_name: harbor-cmp-astro-<trial_id>` line."""
    expected = _expected_astro_name()
    with open(OUTPUT_LOG, "r", encoding="utf-8") as f:
        log_content = f.read()
    pattern = re.compile(
        r"^\s*astro_index_name\s*:\s*" + re.escape(expected) + r"\s*$",
        re.MULTILINE,
    )
    assert pattern.search(log_content), (
        f"Expected {OUTPUT_LOG} to contain a line `astro_index_name: {expected}`, "
        f"but no such line was found.\n"
        f"Log content:\n{log_content!r}"
    )


def test_output_log_contains_cook_index_name_line():
    """The log file must contain a `cook_index_name: harbor-cmp-cook-<trial_id>` line."""
    expected = _expected_cook_name()
    with open(OUTPUT_LOG, "r", encoding="utf-8") as f:
        log_content = f.read()
    pattern = re.compile(
        r"^\s*cook_index_name\s*:\s*" + re.escape(expected) + r"\s*$",
        re.MULTILINE,
    )
    assert pattern.search(log_content), (
        f"Expected {OUTPUT_LOG} to contain a line `cook_index_name: {expected}`, "
        f"but no such line was found.\n"
        f"Log content:\n{log_content!r}"
    )


def test_output_log_contains_composite_retriever_name_line():
    """The log file must contain a `composite_retriever_name: harbor-cmp-retriever-<trial_id>` line."""
    expected = _expected_retriever_name()
    with open(OUTPUT_LOG, "r", encoding="utf-8") as f:
        log_content = f.read()
    pattern = re.compile(
        r"^\s*composite_retriever_name\s*:\s*" + re.escape(expected) + r"\s*$",
        re.MULTILINE,
    )
    assert pattern.search(log_content), (
        f"Expected {OUTPUT_LOG} to contain a line `composite_retriever_name: {expected}`, "
        f"but no such line was found.\n"
        f"Log content:\n{log_content!r}"
    )


def test_output_log_contains_astro_num_retrieved_line():
    """The log file must contain a `astro_num_retrieved: <N>` line with N >= 1."""
    with open(OUTPUT_LOG, "r", encoding="utf-8") as f:
        log_content = f.read()
    match = re.search(
        r"^\s*astro_num_retrieved\s*:\s*(\d+)\s*$",
        log_content,
        re.MULTILINE,
    )
    assert match, (
        f"Expected {OUTPUT_LOG} to contain a line matching "
        f"`astro_num_retrieved: <N>`, but none was found.\n"
        f"Log content:\n{log_content!r}"
    )
    num = int(match.group(1))
    assert num >= 1, f"Expected astro_num_retrieved to be at least 1, got {num}."


def test_output_log_contains_cook_num_retrieved_line():
    """The log file must contain a `cook_num_retrieved: <N>` line with N >= 1."""
    with open(OUTPUT_LOG, "r", encoding="utf-8") as f:
        log_content = f.read()
    match = re.search(
        r"^\s*cook_num_retrieved\s*:\s*(\d+)\s*$",
        log_content,
        re.MULTILINE,
    )
    assert match, (
        f"Expected {OUTPUT_LOG} to contain a line matching "
        f"`cook_num_retrieved: <N>`, but none was found.\n"
        f"Log content:\n{log_content!r}"
    )
    num = int(match.group(1))
    assert num >= 1, f"Expected cook_num_retrieved to be at least 1, got {num}."


def test_astro_managed_index_exists_on_llamacloud():
    """The astronomy managed index must actually exist on the LlamaCloud service."""
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

    expected = _expected_astro_name()
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


def test_cook_managed_index_exists_on_llamacloud():
    """The cooking managed index must actually exist on the LlamaCloud service."""
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

    expected = _expected_cook_name()
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
