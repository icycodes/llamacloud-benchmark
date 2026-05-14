import json
import os
import subprocess

PROJECT_DIR = "/home/user/screenshot_task"
SCRIPT = os.path.join(PROJECT_DIR, "download_screenshots.py")
SCREENSHOTS_DIR = os.path.join(PROJECT_DIR, "screenshots")
MANIFEST = os.path.join(PROJECT_DIR, "manifest.json")
SOURCE_PDF = os.path.join(PROJECT_DIR, "report.pdf")


def _maybe_run_script():
    """If the agent did not leave the manifest in place, re-run the script
    once with the verifier's LLAMA_CLOUD_API_KEY so the artifacts exist for
    the assertions below."""
    if os.path.isfile(MANIFEST):
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


def _load_manifest():
    _maybe_run_script()
    assert os.path.isfile(MANIFEST), \
        f"Expected manifest at {MANIFEST}, but it does not exist."
    with open(MANIFEST, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    assert content.strip() != "", f"Manifest file {MANIFEST} is empty."
    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"Manifest file {MANIFEST} is not valid JSON: {exc}"
        ) from exc
    return data


def test_script_exists():
    assert os.path.isfile(SCRIPT), \
        f"Expected the agent to create {SCRIPT}, but it does not exist."


def test_script_imports_llama_cloud():
    with open(SCRIPT, "r", encoding="utf-8", errors="replace") as f:
        contents = f.read()
    assert "from llama_cloud import LlamaCloud" in contents, (
        "download_screenshots.py must import LlamaCloud from llama_cloud."
    )


def test_script_invokes_parsing_parse_exactly_once():
    with open(SCRIPT, "r", encoding="utf-8", errors="replace") as f:
        contents = f.read()
    count = contents.count("parsing.parse(")
    assert count == 1, (
        f"download_screenshots.py must invoke client.parsing.parse(...) "
        f"exactly once; found {count} occurrences of 'parsing.parse('."
    )


def test_script_requests_screenshots_and_images_metadata():
    with open(SCRIPT, "r", encoding="utf-8", errors="replace") as f:
        contents = f.read()
    assert "images_to_save" in contents, (
        "download_screenshots.py must pass images_to_save to parsing.parse "
        "(via output_options)."
    )
    assert '"screenshot"' in contents or "'screenshot'" in contents, (
        "download_screenshots.py must request the 'screenshot' image kind in "
        "output_options.images_to_save."
    )
    assert "images_content_metadata" in contents, (
        "download_screenshots.py must request the 'images_content_metadata' "
        "expand value to retrieve presigned image URLs."
    )


def test_script_does_not_hardcode_api_key():
    with open(SCRIPT, "r", encoding="utf-8", errors="replace") as f:
        contents = f.read()
    assert "llx-" not in contents, (
        "download_screenshots.py must not hardcode a LlamaCloud API key "
        "(found 'llx-' literal in the file)."
    )


def test_screenshots_dir_exists_and_non_empty():
    _maybe_run_script()
    assert os.path.isdir(SCREENSHOTS_DIR), \
        f"Expected screenshots directory at {SCREENSHOTS_DIR}, but it is missing."
    entries = [
        e for e in os.listdir(SCREENSHOTS_DIR)
        if os.path.isfile(os.path.join(SCREENSHOTS_DIR, e))
    ]
    assert len(entries) >= 1, (
        f"Expected at least one image file inside {SCREENSHOTS_DIR}, "
        f"but found none."
    )


def test_every_screenshot_file_is_a_valid_image():
    _maybe_run_script()
    assert os.path.isdir(SCREENSHOTS_DIR), \
        f"Expected screenshots directory at {SCREENSHOTS_DIR}, but it is missing."
    png_sig = b"\x89PNG\r\n\x1a\n"
    jpeg_sig = b"\xff\xd8\xff"
    for name in sorted(os.listdir(SCREENSHOTS_DIR)):
        path = os.path.join(SCREENSHOTS_DIR, name)
        if not os.path.isfile(path):
            continue
        assert os.path.getsize(path) > 0, \
            f"Screenshot file {path} is empty."
        with open(path, "rb") as f:
            header = f.read(8)
        assert header.startswith(png_sig) or header.startswith(jpeg_sig), (
            f"Screenshot file {path} is not a valid PNG or JPEG "
            f"(unexpected header bytes: {header!r})."
        )


def test_manifest_top_level_keys():
    data = _load_manifest()
    for key in ("source", "job_id", "page_count", "image_count", "images"):
        assert key in data, \
            f"Manifest JSON is missing required top-level key '{key}'."


def test_manifest_source_value():
    data = _load_manifest()
    assert data.get("source") == "report.pdf", \
        f"Expected source == 'report.pdf', got {data.get('source')!r}."


def test_manifest_page_count_is_three():
    data = _load_manifest()
    page_count = data.get("page_count")
    assert isinstance(page_count, int), \
        f"page_count must be an integer, got {type(page_count).__name__}."
    assert page_count == 3, \
        f"Expected page_count == 3, got {page_count}."


def test_manifest_job_id_shape():
    data = _load_manifest()
    job_id = data.get("job_id")
    assert isinstance(job_id, str) and len(job_id.strip()) >= 8, (
        f"Expected job_id to be a non-empty string of length >= 8, "
        f"got {job_id!r}."
    )


def test_manifest_image_count_matches_images_length():
    data = _load_manifest()
    image_count = data.get("image_count")
    images = data.get("images")
    assert isinstance(image_count, int) and image_count >= 1, \
        f"image_count must be an integer >= 1, got {image_count!r}."
    assert isinstance(images, list), \
        f"images must be a list, got {type(images).__name__}."
    assert image_count == len(images), (
        f"image_count ({image_count}) must equal len(images) ({len(images)})."
    )


def test_manifest_image_count_matches_disk_files():
    data = _load_manifest()
    image_count = data["image_count"]
    on_disk = [
        e for e in os.listdir(SCREENSHOTS_DIR)
        if os.path.isfile(os.path.join(SCREENSHOTS_DIR, e))
    ]
    assert len(on_disk) == image_count, (
        f"Number of files in {SCREENSHOTS_DIR} ({len(on_disk)}) must equal "
        f"manifest.image_count ({image_count})."
    )


def test_manifest_entries_shape_and_size_match_disk():
    data = _load_manifest()
    for idx, entry in enumerate(data["images"]):
        assert isinstance(entry, dict), \
            f"images[{idx}] must be a JSON object, got {type(entry).__name__}."
        filename = entry.get("filename")
        size_bytes = entry.get("size_bytes")
        saved_path = entry.get("saved_path")
        assert isinstance(filename, str) and filename.strip() != "", \
            f"images[{idx}]['filename'] must be a non-empty string, got {filename!r}."
        assert isinstance(size_bytes, int) and size_bytes >= 0, \
            f"images[{idx}]['size_bytes'] must be a non-negative integer, got {size_bytes!r}."
        assert isinstance(saved_path, str) and saved_path.strip() != "", \
            f"images[{idx}]['saved_path'] must be a non-empty string, got {saved_path!r}."
        assert os.path.isfile(saved_path), \
            f"images[{idx}]['saved_path'] = {saved_path} does not point to a real file."
        actual_size = os.path.getsize(saved_path)
        assert actual_size == size_bytes, (
            f"images[{idx}]['size_bytes'] ({size_bytes}) does not match the "
            f"actual on-disk size of {saved_path} ({actual_size})."
        )


def test_job_id_is_real_on_llamacloud():
    """Confirm the recorded job_id corresponds to a real, COMPLETED parse job
    on the LlamaCloud server, by invoking the SDK from a subprocess so this
    file stays stdlib-only."""
    data = _load_manifest()
    job_id = data["job_id"]
    code = (
        "import json,os,sys;"
        "from llama_cloud import LlamaCloud;"
        "c=LlamaCloud();"
        f"r=c.parsing.get(job_id={job_id!r}, expand=['job_metadata']);"
        "status=getattr(getattr(r,'job',None),'status',None);"
        "print(json.dumps({'status': str(status) if status is not None else ''}))"
    )
    result = subprocess.run(
        ["python3", "-c", code],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, (
        f"Looking up job_id={job_id!r} via LlamaCloud SDK failed.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    try:
        payload = json.loads(result.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError) as exc:
        raise AssertionError(
            f"Could not parse SDK lookup output as JSON: {result.stdout!r}"
        ) from exc
    status = (payload.get("status") or "").strip().lower()
    # status from the SDK can be an enum repr; accept anything that contains 'completed'.
    assert "completed" in status, (
        f"Expected the recorded job to be COMPLETED on LlamaCloud, "
        f"got status={status!r}."
    )


def test_source_pdf_unchanged():
    assert os.path.isfile(SOURCE_PDF), \
        f"Source PDF {SOURCE_PDF} must remain in place."
    with open(SOURCE_PDF, "rb") as f:
        header = f.read(5)
    assert header.startswith(b"%PDF-"), \
        f"Source PDF {SOURCE_PDF} is no longer a valid PDF."
