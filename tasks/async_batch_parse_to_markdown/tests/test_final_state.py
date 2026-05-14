import os

PROJECT_DIR = "/home/user/batch_parse"
SCRIPT_PATH = os.path.join(PROJECT_DIR, "batch_parse.py")
OUT_DIR = os.path.join(PROJECT_DIR, "out")

REPORTS = (
    ("alpha.md", "Alpha Project Report"),
    ("bravo.md", "Bravo Project Report"),
    ("charlie.md", "Charlie Project Report"),
)

ALL_MARKERS = tuple(marker for _, marker in REPORTS)


def _read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def test_batch_parse_script_exists():
    assert os.path.isfile(SCRIPT_PATH), (
        f"Expected the user's batch parsing script at {SCRIPT_PATH}, but it was not found."
    )


def test_batch_parse_script_uses_async_llama_cloud_sdk():
    content = _read_text(SCRIPT_PATH)
    assert "from llama_cloud import AsyncLlamaCloud" in content, (
        f"{SCRIPT_PATH} must import AsyncLlamaCloud from the llama_cloud SDK "
        "(expected the literal substring `from llama_cloud import AsyncLlamaCloud`)."
    )
    assert "parsing.parse(" in content, (
        f"{SCRIPT_PATH} must invoke client.parsing.parse(...) to start a LlamaParse job."
    )


def test_batch_parse_script_uses_asyncio_gather():
    content = _read_text(SCRIPT_PATH)
    assert "asyncio.gather" in content, (
        f"{SCRIPT_PATH} must drive parses concurrently with asyncio.gather "
        "(expected the substring `asyncio.gather`)."
    )


def test_batch_parse_script_does_not_use_sync_client():
    content = _read_text(SCRIPT_PATH)
    assert "from llama_cloud import LlamaCloud" not in content, (
        f"{SCRIPT_PATH} must use the asynchronous AsyncLlamaCloud client, "
        "not the synchronous LlamaCloud client. Remove "
        "`from llama_cloud import LlamaCloud`."
    )


def test_batch_parse_script_does_not_hardcode_api_key():
    content = _read_text(SCRIPT_PATH)
    assert "llx-" not in content, (
        f"{SCRIPT_PATH} appears to hardcode a LlamaCloud API key (found 'llx-' prefix). "
        "The script must rely on the LLAMA_CLOUD_API_KEY environment variable."
    )


def test_output_directory_exists():
    assert os.path.isdir(OUT_DIR), (
        f"Expected output directory {OUT_DIR} to exist after the task is executed."
    )


def test_each_output_markdown_exists_and_nonempty():
    for filename, _ in REPORTS:
        out_path = os.path.join(OUT_DIR, filename)
        assert os.path.isfile(out_path), (
            f"Expected output markdown file {out_path} to exist."
        )
        assert os.path.getsize(out_path) > 0, (
            f"Output markdown file {out_path} exists but is empty."
        )


def test_each_output_markdown_contains_its_own_marker():
    for filename, marker in REPORTS:
        out_path = os.path.join(OUT_DIR, filename)
        content = _read_text(out_path).lower()
        assert marker.lower() in content, (
            f"Output markdown {out_path} must contain the marker '{marker}' "
            f"from its corresponding source PDF (case-insensitive). Got first 200 chars: "
            f"{content[:200]!r}"
        )


def test_each_output_markdown_excludes_other_markers():
    for filename, own_marker in REPORTS:
        out_path = os.path.join(OUT_DIR, filename)
        content = _read_text(out_path).lower()
        for other_marker in ALL_MARKERS:
            if other_marker == own_marker:
                continue
            assert other_marker.lower() not in content, (
                f"Output markdown {out_path} unexpectedly contains the marker "
                f"'{other_marker}' which belongs to a different source PDF. "
                "Each output file must only contain the parsed content of its "
                "matching input PDF."
            )
