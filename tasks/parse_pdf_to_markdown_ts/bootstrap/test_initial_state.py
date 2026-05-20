import os
import shutil
import subprocess

PROJECT_DIR = "/home/user/parse_task_ts"
SAMPLE_PDF = os.path.join(PROJECT_DIR, "sample.pdf")


def test_node_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."


def test_npx_available():
    assert shutil.which("npx") is not None, "npx binary not found in PATH."


def test_tsx_available():
    """tsx must be globally available for `npx tsx parse.ts` execution."""
    result = subprocess.run(
        ["npx", "--no-install", "tsx", "--version"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Failed to invoke 'npx tsx --version': stdout={result.stdout!r} stderr={result.stderr!r}"
    )


def test_llama_cloud_ts_sdk_installed():
    """The @llamaindex/llama-cloud SDK must already be globally available so the
    executor can require/import it from inside the project directory."""
    # Resolve through Node from PROJECT_DIR so any local node_modules also work.
    result = subprocess.run(
        ["node", "-e", "require.resolve('@llamaindex/llama-cloud')"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        "@llamaindex/llama-cloud could not be resolved from "
        f"{PROJECT_DIR}: stdout={result.stdout!r} stderr={result.stderr!r}"
    )


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_sample_pdf_exists():
    assert os.path.isfile(SAMPLE_PDF), (
        f"Expected pre-seeded PDF at {SAMPLE_PDF} was not found."
    )


def test_sample_pdf_is_a_pdf():
    """Verify the seeded file is a real PDF (magic bytes)."""
    with open(SAMPLE_PDF, "rb") as fp:
        header = fp.read(4)
    assert header == b"%PDF", (
        f"File at {SAMPLE_PDF} does not look like a PDF (got header {header!r})."
    )


def test_output_md_not_pre_created():
    """The executor must create the output file; it must not exist initially."""
    output_md = os.path.join(PROJECT_DIR, "output.md")
    assert not os.path.exists(output_md), (
        f"{output_md} should not exist at task start; the executor must create it."
    )


def test_parse_script_not_pre_created():
    """The executor must create parse.ts; it must not exist initially."""
    parse_ts = os.path.join(PROJECT_DIR, "parse.ts")
    assert not os.path.exists(parse_ts), (
        f"{parse_ts} should not exist at task start; the executor must create it."
    )
