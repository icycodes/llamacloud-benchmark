import json
import os
import subprocess

PROJECT_DIR = "/home/user/myproject"
SCRIPT = os.path.join(PROJECT_DIR, "build_inventory.py")
INVENTORY = os.path.join(PROJECT_DIR, "inventory.json")
SOURCE_PDF = os.path.join(PROJECT_DIR, "report.pdf")


def _maybe_run_build_script():
    """If the agent did not leave the inventory file in place, re-run the
    script once with the verifier's LLAMA_CLOUD_API_KEY so the artifact is
    present for the assertions below."""
    if os.path.isfile(INVENTORY):
        return
    if not os.path.isfile(SCRIPT):
        return
    subprocess.run(
        ["python3", SCRIPT],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=600,
    )


def _load_inventory():
    _maybe_run_build_script()
    assert os.path.isfile(INVENTORY), \
        f"Expected inventory at {INVENTORY}, but it does not exist."
    with open(INVENTORY, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    assert content.strip() != "", \
        f"Inventory file {INVENTORY} is empty."
    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"Inventory file {INVENTORY} is not valid JSON: {exc}"
        ) from exc
    return data


def test_build_script_exists():
    assert os.path.isfile(SCRIPT), \
        f"Expected the agent to create {SCRIPT}, but it does not exist."


def test_build_script_uses_llamaparse_sdk():
    with open(SCRIPT, "r", encoding="utf-8", errors="replace") as f:
        contents = f.read()
    references = (
        "llama_cloud_services" in contents
        or "llama_cloud" in contents
        or "LlamaCloud" in contents
        or "LlamaParse" in contents
    )
    assert references, (
        "build_inventory.py must import or reference a LlamaParse client from "
        "either 'llama_cloud_services' or 'llama_cloud'."
    )


def test_inventory_file_exists_and_non_empty():
    _maybe_run_build_script()
    assert os.path.isfile(INVENTORY), \
        f"Expected inventory at {INVENTORY}, but it does not exist."
    assert os.path.getsize(INVENTORY) > 0, \
        f"Inventory file {INVENTORY} is empty."


def test_inventory_top_level_keys():
    data = _load_inventory()
    for key in ("source", "page_count", "item_count", "by_type", "items"):
        assert key in data, \
            f"Inventory JSON is missing required top-level key '{key}'."


def test_inventory_source_value():
    data = _load_inventory()
    assert data.get("source") == "report.pdf", \
        f"Expected source == 'report.pdf', got {data.get('source')!r}."


def test_inventory_page_count_is_three():
    data = _load_inventory()
    page_count = data.get("page_count")
    assert isinstance(page_count, int), \
        f"page_count must be an integer, got {type(page_count).__name__}: {page_count!r}"
    assert page_count == 3, \
        f"Expected page_count == 3 (the source PDF has 3 pages), got {page_count}."


def test_inventory_items_non_empty_list():
    data = _load_inventory()
    items = data.get("items")
    assert isinstance(items, list), \
        f"items must be a JSON list, got {type(items).__name__}."
    assert len(items) > 0, "items list must be non-empty."


def test_inventory_item_count_matches_items_length():
    data = _load_inventory()
    item_count = data.get("item_count")
    items = data.get("items")
    assert isinstance(item_count, int), \
        f"item_count must be an integer, got {type(item_count).__name__}."
    assert item_count == len(items), \
        f"item_count ({item_count}) must equal len(items) ({len(items)})."


def test_inventory_item_entry_shape():
    data = _load_inventory()
    items = data["items"]
    page_count = data["page_count"]
    for idx, entry in enumerate(items):
        assert isinstance(entry, dict), \
            f"items[{idx}] must be a JSON object, got {type(entry).__name__}."
        page = entry.get("page")
        type_str = entry.get("type")
        value = entry.get("value")
        assert isinstance(page, int), \
            f"items[{idx}]['page'] must be an integer, got {type(page).__name__}: {page!r}."
        assert 1 <= page <= page_count, \
            f"items[{idx}]['page'] = {page} must be in [1, {page_count}]."
        assert isinstance(type_str, str) and type_str.strip() != "", \
            f"items[{idx}]['type'] must be a non-empty string, got {type_str!r}."
        assert isinstance(value, str) and value.strip() != "", \
            f"items[{idx}]['value'] must be a non-empty string, got {value!r}."


def test_inventory_items_sorted_by_page():
    data = _load_inventory()
    pages = [entry["page"] for entry in data["items"]]
    assert pages == sorted(pages), \
        f"items must be sorted by ascending page; got page sequence: {pages}."


def test_inventory_by_type_shape_and_sum():
    data = _load_inventory()
    by_type = data.get("by_type")
    items = data["items"]
    assert isinstance(by_type, dict), \
        f"by_type must be a JSON object, got {type(by_type).__name__}."
    # Every value must be a non-negative int.
    for k, v in by_type.items():
        assert isinstance(k, str) and k.strip() != "", \
            f"by_type keys must be non-empty strings, got {k!r}."
        assert isinstance(v, int) and v >= 0, \
            f"by_type[{k!r}] must be a non-negative integer, got {v!r}."
    # Sum of values must equal item_count.
    total = sum(by_type.values())
    assert total == len(items), \
        f"Sum of by_type values ({total}) must equal len(items) ({len(items)})."
    # Every type appearing in items must be a key in by_type, with the right count.
    expected_counts = {}
    for entry in items:
        expected_counts[entry["type"]] = expected_counts.get(entry["type"], 0) + 1
    for t, count in expected_counts.items():
        assert t in by_type, \
            f"Type {t!r} appears in items but is missing from by_type."
        assert by_type[t] == count, (
            f"by_type[{t!r}] = {by_type[t]} does not match the actual count "
            f"{count} of type {t!r} in items."
        )


def _concatenated_item_values(data):
    return "\n".join(entry["value"] for entry in data["items"])


def test_inventory_contains_page1_section_title():
    data = _load_inventory()
    blob = _concatenated_item_values(data)
    assert "Project Phoenix Overview" in blob, (
        "Expected the inventory to contain the section title "
        "'Project Phoenix Overview' (printed on page 1 of the source PDF)."
    )


def test_inventory_contains_page2_section_title():
    data = _load_inventory()
    blob = _concatenated_item_values(data)
    assert "Implementation Roadmap" in blob, (
        "Expected the inventory to contain the section title "
        "'Implementation Roadmap' (printed on page 2 of the source PDF)."
    )


def test_inventory_contains_page3_section_title():
    data = _load_inventory()
    blob = _concatenated_item_values(data)
    assert "Risk Assessment Summary" in blob, (
        "Expected the inventory to contain the section title "
        "'Risk Assessment Summary' (printed on page 3 of the source PDF)."
    )


def test_inventory_page1_title_is_on_page_one():
    data = _load_inventory()
    matches = [
        entry for entry in data["items"]
        if "Project Phoenix Overview" in entry["value"]
    ]
    assert matches, "'Project Phoenix Overview' must appear in at least one item."
    assert all(entry["page"] == 1 for entry in matches), (
        "'Project Phoenix Overview' must only appear on page 1, but it was found "
        f"on pages: {[e['page'] for e in matches]}."
    )


def test_inventory_page2_title_is_on_page_two():
    data = _load_inventory()
    matches = [
        entry for entry in data["items"]
        if "Implementation Roadmap" in entry["value"]
    ]
    assert matches, "'Implementation Roadmap' must appear in at least one item."
    assert all(entry["page"] == 2 for entry in matches), (
        "'Implementation Roadmap' must only appear on page 2, but it was found "
        f"on pages: {[e['page'] for e in matches]}."
    )


def test_inventory_page3_title_is_on_page_three():
    data = _load_inventory()
    matches = [
        entry for entry in data["items"]
        if "Risk Assessment Summary" in entry["value"]
    ]
    assert matches, "'Risk Assessment Summary' must appear in at least one item."
    assert all(entry["page"] == 3 for entry in matches), (
        "'Risk Assessment Summary' must only appear on page 3, but it was found "
        f"on pages: {[e['page'] for e in matches]}."
    )


def test_source_pdf_unchanged():
    assert os.path.isfile(SOURCE_PDF), \
        f"Source PDF {SOURCE_PDF} must remain in place."
    with open(SOURCE_PDF, "rb") as f:
        header = f.read(5)
    assert header.startswith(b"%PDF-"), \
        f"Source PDF {SOURCE_PDF} is no longer a valid PDF."
