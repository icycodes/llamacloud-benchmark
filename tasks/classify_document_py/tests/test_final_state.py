import json
import os
import subprocess

PROJECT_DIR = "/home/user/myproject"
SCRIPT = os.path.join(PROJECT_DIR, "classify.py")
INPUT_FILE = os.path.join(PROJECT_DIR, "document.txt")
OUTPUT_FILE = os.path.join(PROJECT_DIR, "classification.json")


def _run_classify(input_path: str, output_path: str):
    """Run the agent's classify.py with the given input/output paths."""
    return subprocess.run(
        ["python3", SCRIPT, "--input", input_path, "--output", output_path],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
        timeout=600,
    )


def test_script_runs_successfully_and_prints_classification():
    """Pre-clean the output file, then run classify.py and verify success + stdout line."""
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)

    result = _run_classify(INPUT_FILE, OUTPUT_FILE)
    assert result.returncode == 0, (
        f"classify.py exited with non-zero status {result.returncode}. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    stdout_lines = [line.strip() for line in result.stdout.splitlines()]
    expected_line = "Classified as: invoice"
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

    classified_type = data.get("type")
    confidence = data.get("confidence")
    reasoning = data.get("reasoning")

    assert (
        isinstance(classified_type, str)
        and classified_type.strip().lower() == "invoice"
    ), (
        f"Expected type == 'invoice' (case-insensitive), got: {classified_type!r}"
    )
    assert confidence is not None, (
        f"Expected 'confidence' field to be present in the output JSON, got: {data!r}"
    )
    assert isinstance(reasoning, str) and reasoning.strip(), (
        f"Expected 'reasoning' to be a non-empty string, got: {reasoning!r}"
    )


def test_script_uses_required_sdk_constructs():
    """Static inspection: the script must use the required SDK calls and rules."""
    assert os.path.isfile(SCRIPT), f"Script not found at {SCRIPT}"
    with open(SCRIPT, "r", encoding="utf-8") as f:
        source = f.read()

    assert "from llama_cloud import LlamaCloud" in source, (
        "Expected the script to import LlamaCloud via 'from llama_cloud import LlamaCloud'."
    )
    assert 'purpose="classify"' in source or "purpose='classify'" in source, (
        "Expected the script to pass purpose=\"classify\" to client.files.create."
    )
    assert 'mode="FAST"' in source or "mode='FAST'" in source, (
        "Expected the script to pass mode=\"FAST\" to client.classifier.classify."
    )
    assert '"invoice"' in source or "'invoice'" in source, (
        "Expected the script source to include the 'invoice' classification rule type."
    )
    assert '"receipt"' in source or "'receipt'" in source, (
        "Expected the script source to include the 'receipt' classification rule type."
    )


def test_script_fails_with_missing_input():
    """Re-running with a non-existent input must produce a non-zero exit code."""
    missing_input = os.path.join(PROJECT_DIR, "does_not_exist.txt")
    result = _run_classify(missing_input, OUTPUT_FILE)
    assert result.returncode != 0, (
        f"Expected non-zero exit code when --input does not exist, got 0. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
