import json
import os
import subprocess

import pytest

PROJECT_DIR = "/home/user/parse_payload"
SCRIPT_PATH = os.path.join(PROJECT_DIR, "build_payload.py")
OUTPUT_PATH = os.path.join(PROJECT_DIR, "request_body.json")

EXPECTED_PAYLOAD = {
    "file_id": "file-demo-abc-123",
    "tier": "agentic",
    "version": "latest",
    "disable_cache": False,
    "page_ranges": {"target_pages": "1-3,5"},
    "crop_box": {"top": 0.1, "bottom": 0.15},
    "processing_options": {
        "ocr_parameters": {"languages": ["en", "fr"]},
        "cost_optimizer": {"enable": True},
        "ignore": {"ignore_diagonal_text": True},
    },
    "agentic_options": {
        "custom_prompt": "This is a financial report. Preserve currency symbols."
    },
    "output_options": {
        "markdown": {"tables": {"output_tables_as_markdown": False}},
        "images_to_save": ["screenshot"],
    },
    "processing_control": {
        "timeouts": {
            "base_in_seconds": 300,
            "extra_time_per_page_in_seconds": 30,
        },
    },
}

EXPECTED_TOP_LEVEL_KEYS = sorted(
    [
        "agentic_options",
        "crop_box",
        "disable_cache",
        "file_id",
        "output_options",
        "page_ranges",
        "processing_control",
        "processing_options",
        "tier",
        "version",
    ]
)


def _walk_keys(node):
    """Yield every dict key that appears anywhere in a parsed JSON tree."""
    if isinstance(node, dict):
        for k, v in node.items():
            yield k
            yield from _walk_keys(v)
    elif isinstance(node, list):
        for item in node:
            yield from _walk_keys(item)


@pytest.fixture(scope="module")
def script_run():
    """Run the agent's build_payload.py exactly once and capture its output."""
    assert os.path.isfile(SCRIPT_PATH), (
        f"Expected {SCRIPT_PATH} to exist before running final-state verification."
    )
    result = subprocess.run(
        ["python3", "build_payload.py"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=60,
    )
    return result


def test_script_exists():
    assert os.path.isfile(SCRIPT_PATH), (
        f"Expected {SCRIPT_PATH} to be created by the agent."
    )


def test_script_uses_llama_cloud_sdk():
    with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    assert "from llama_cloud import LlamaCloud" in content, (
        f"{SCRIPT_PATH} must contain 'from llama_cloud import LlamaCloud'."
    )


def test_script_does_not_hardcode_api_key():
    with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    assert "llx-" not in content, (
        f"{SCRIPT_PATH} appears to hardcode a LlamaCloud API key (found 'llx-' prefix). "
        "It must rely on LLAMA_CLOUD_API_KEY from the environment."
    )


def test_script_makes_no_network_calls():
    with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    forbidden = [
        "parsing.parse(",
        "files.create(",
        "requests.",
        "httpx.",
        "urllib.request",
        "curl ",
    ]
    for needle in forbidden:
        assert needle not in content, (
            f"{SCRIPT_PATH} must not make network calls. "
            f"Forbidden substring found: {needle!r}."
        )


def test_script_does_not_mention_expand():
    with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    assert '"expand"' not in content and "'expand'" not in content, (
        f"{SCRIPT_PATH} must not place an 'expand' field in the parse request body. "
        "`expand` is a query parameter on the GET result endpoint, not part of the body."
    )


def test_script_runs_successfully(script_run):
    assert script_run.returncode == 0, (
        f"python3 build_payload.py exited with code {script_run.returncode}. "
        f"stdout: {script_run.stdout!r}, stderr: {script_run.stderr!r}"
    )


def test_script_prints_expected_summary(script_run):
    expected = "payload_ok file_id=file-demo-abc-123 tier=agentic top_level_keys=10"
    assert script_run.stdout.strip() == expected, (
        f"build_payload.py stdout must equal {expected!r}, got: {script_run.stdout!r}"
    )


def test_request_body_exists(script_run):
    assert os.path.isfile(OUTPUT_PATH), (
        f"Expected {OUTPUT_PATH} to be created by build_payload.py."
    )


def test_request_body_matches_expected(script_run):
    with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data == EXPECTED_PAYLOAD, (
        f"{OUTPUT_PATH} contents do not match the expected payload.\n"
        f"Expected: {EXPECTED_PAYLOAD!r}\nGot: {data!r}"
    )


def test_request_body_top_level_keys(script_run):
    with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    actual_keys = sorted(data.keys())
    assert actual_keys == EXPECTED_TOP_LEVEL_KEYS, (
        f"Top-level keys mismatch.\nExpected: {EXPECTED_TOP_LEVEL_KEYS!r}\n"
        f"Got:      {actual_keys!r}"
    )
    assert len(data) == 10, (
        f"Payload must have exactly 10 top-level keys, got {len(data)}: {actual_keys!r}"
    )


def test_request_body_top_level_keys_are_alphabetically_sorted(script_run):
    """Re-read the JSON file as text and verify the on-disk order of top-level keys."""
    decoder = json.JSONDecoder(object_pairs_hook=list)
    with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
        pairs = decoder.decode(f.read())
    assert isinstance(pairs, list), (
        f"{OUTPUT_PATH} top-level must be a JSON object. Got: {type(pairs).__name__}"
    )
    on_disk_keys = [k for k, _v in pairs]
    assert on_disk_keys == sorted(on_disk_keys), (
        f"Top-level keys in {OUTPUT_PATH} must be sorted alphabetically as written. "
        f"Got order: {on_disk_keys!r}"
    )


def test_request_body_has_no_expand_anywhere(script_run):
    with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    all_keys = set(_walk_keys(data))
    assert "expand" not in all_keys, (
        f"{OUTPUT_PATH} must not contain an 'expand' key at any nesting level. "
        f"All keys found: {sorted(all_keys)!r}"
    )


def test_custom_prompt_is_under_agentic_options(script_run):
    with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "agentic_options" in data, "Missing top-level 'agentic_options' key."
    assert isinstance(data["agentic_options"], dict), (
        "'agentic_options' must be a JSON object."
    )
    assert "custom_prompt" in data["agentic_options"], (
        "'custom_prompt' must live under 'agentic_options'."
    )
    assert data["agentic_options"]["custom_prompt"] == (
        "This is a financial report. Preserve currency symbols."
    ), (
        f"'agentic_options.custom_prompt' has unexpected value: "
        f"{data['agentic_options']['custom_prompt']!r}"
    )
    proc_opts = data.get("processing_options", {})
    assert "custom_prompt" not in proc_opts, (
        "'custom_prompt' MUST NOT appear under 'processing_options'. "
        "It belongs under 'agentic_options'."
    )


def test_timeouts_is_under_processing_control(script_run):
    with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "processing_control" in data, "Missing top-level 'processing_control' key."
    pc = data["processing_control"]
    assert isinstance(pc, dict) and "timeouts" in pc, (
        "'processing_control.timeouts' must exist."
    )
    assert pc["timeouts"] == {
        "base_in_seconds": 300,
        "extra_time_per_page_in_seconds": 30,
    }, f"'processing_control.timeouts' has unexpected value: {pc['timeouts']!r}"
    proc_opts = data.get("processing_options", {})
    assert "timeouts" not in proc_opts, (
        "'timeouts' MUST NOT appear under 'processing_options'. "
        "It belongs under 'processing_control'."
    )


def test_page_ranges_and_crop_box_are_top_level(script_run):
    with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "page_ranges" in data, "'page_ranges' must be a top-level key."
    assert data["page_ranges"] == {"target_pages": "1-3,5"}, (
        f"'page_ranges' has unexpected value: {data['page_ranges']!r}"
    )
    assert "crop_box" in data, "'crop_box' must be a top-level key."
    assert data["crop_box"] == {"top": 0.1, "bottom": 0.15}, (
        f"'crop_box' has unexpected value: {data['crop_box']!r}"
    )
    proc_opts = data.get("processing_options", {})
    assert "page_ranges" not in proc_opts, (
        "'page_ranges' MUST NOT be nested under 'processing_options'."
    )
    assert "crop_box" not in proc_opts, (
        "'crop_box' MUST NOT be nested under 'processing_options'."
    )


def test_output_options_tables_negated_correctly(script_run):
    with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    md = data.get("output_options", {}).get("markdown", {})
    tables = md.get("tables", {})
    assert tables.get("output_tables_as_markdown") is False, (
        "Intent had `tables_as_html=true`, so "
        "'output_options.markdown.tables.output_tables_as_markdown' must be False. "
        f"Got: {tables!r}"
    )


def test_output_options_images_to_save_included(script_run):
    with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    out_opts = data.get("output_options", {})
    assert out_opts.get("images_to_save") == ["screenshot"], (
        "Intent had `save_screenshots=true`, so "
        "'output_options.images_to_save' must equal ['screenshot']. "
        f"Got: {out_opts.get('images_to_save')!r}"
    )


def test_processing_options_nested_fields(script_run):
    with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    po = data.get("processing_options", {})
    assert po.get("ocr_parameters") == {"languages": ["en", "fr"]}, (
        f"'processing_options.ocr_parameters' must equal "
        f"{{'languages': ['en', 'fr']}}. Got: {po.get('ocr_parameters')!r}"
    )
    assert po.get("cost_optimizer") == {"enable": True}, (
        f"'processing_options.cost_optimizer' must equal {{'enable': True}}. "
        f"Got: {po.get('cost_optimizer')!r}"
    )
    assert po.get("ignore") == {"ignore_diagonal_text": True}, (
        f"'processing_options.ignore' must equal {{'ignore_diagonal_text': True}}. "
        f"Got: {po.get('ignore')!r}"
    )
