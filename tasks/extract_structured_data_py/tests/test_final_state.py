import json
import os
import subprocess

PROJECT_DIR = "/home/user/myproject"
SCRIPT = os.path.join(PROJECT_DIR, "extract.py")
INPUT_FILE = os.path.join(PROJECT_DIR, "candidate.txt")
OUTPUT_FILE = os.path.join(PROJECT_DIR, "candidate.json")


def _run_extract(input_path: str, output_path: str):
    """Run the agent's extract.py with the given input/output paths."""
    return subprocess.run(
        ["python3", SCRIPT, "--input", input_path, "--output", output_path],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
        timeout=600,
    )


def test_script_runs_successfully_and_prints_candidate_name():
    """Pre-clean the output file, then run extract.py and verify success + stdout line."""
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)

    result = _run_extract(INPUT_FILE, OUTPUT_FILE)
    assert result.returncode == 0, (
        f"extract.py exited with non-zero status {result.returncode}. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    stdout_lines = [line.strip() for line in result.stdout.splitlines()]
    expected_line = "Extracted candidate: Alice Johnson"
    assert expected_line in stdout_lines, (
        f"Expected stdout to contain a line {expected_line!r}, "
        f"got stdout={result.stdout!r}"
    )


def test_output_json_file_exists():
    assert os.path.isfile(OUTPUT_FILE), (
        f"Expected output JSON file at {OUTPUT_FILE}, but it does not exist."
    )


def test_output_json_is_valid_and_has_expected_fields():
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        raw = f.read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise AssertionError(
            f"Output file {OUTPUT_FILE} is not valid JSON: {e}. content={raw!r}"
        )
    assert isinstance(data, dict), (
        f"Expected the top-level JSON value to be an object, got: {type(data).__name__}"
    )

    name = data.get("name")
    email = data.get("email")
    skills = data.get("skills")

    assert isinstance(name, str) and name.strip().lower() == "alice johnson", (
        f"Expected name == 'Alice Johnson' (case-insensitive), got: {name!r}"
    )
    assert (
        isinstance(email, str)
        and email.strip().lower() == "alice.johnson@example.com"
    ), (
        f"Expected email == 'alice.johnson@example.com' (case-insensitive), got: {email!r}"
    )
    assert isinstance(skills, list), (
        f"Expected 'skills' to be a list, got: {type(skills).__name__} ({skills!r})"
    )
    normalized = {str(s).strip().lower() for s in skills if isinstance(s, (str, int, float))}
    for expected in ("python", "machine learning", "docker", "kubernetes"):
        assert expected in normalized, (
            f"Expected skill {expected!r} to appear (case-insensitively) in extracted skills, "
            f"got: {skills!r}"
        )


def test_script_uses_required_sdk_and_pydantic_constructs():
    """Static inspection: the script must use the required SDK calls and Pydantic schema."""
    assert os.path.isfile(SCRIPT), f"Script not found at {SCRIPT}"
    with open(SCRIPT, "r", encoding="utf-8") as f:
        source = f.read()

    assert "from llama_cloud import LlamaCloud" in source, (
        "Expected the script to import LlamaCloud via 'from llama_cloud import LlamaCloud'."
    )
    assert "class Candidate(BaseModel):" in source, (
        "Expected the script to define a Pydantic model named 'Candidate' "
        "(line matching 'class Candidate(BaseModel):')."
    )
    assert 'extraction_target="per_doc"' in source or "extraction_target='per_doc'" in source, (
        "Expected the script to pass extraction_target=\"per_doc\" to client.extract.create."
    )
    assert 'tier="agentic"' in source or "tier='agentic'" in source, (
        "Expected the script to pass tier=\"agentic\" to client.extract.create."
    )
    assert "model_json_schema()" in source, (
        "Expected the script to derive the schema using Candidate.model_json_schema()."
    )


def test_script_fails_with_missing_input():
    """Re-running with a non-existent input must produce a non-zero exit code."""
    missing_input = os.path.join(PROJECT_DIR, "does_not_exist.txt")
    result = _run_extract(missing_input, OUTPUT_FILE)
    assert result.returncode != 0, (
        f"Expected non-zero exit code when --input does not exist, got 0. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
