import json
import os
import re
import subprocess


PROJECT_DIR = "/home/user/myproject"
FIXTURE_PDF = os.path.join(PROJECT_DIR, "fixtures", "sample.pdf")
PACKAGE_JSON = os.path.join(PROJECT_DIR, "package.json")
OUTPUT_MD = os.path.join(PROJECT_DIR, "output.md")
MISSING_KEY_MD = os.path.join(PROJECT_DIR, "missing-key.md")
MISSING_INPUT_MD = os.path.join(PROJECT_DIR, "missing-input.md")

PARSE_TIMEOUT = 360


def _cleanup_output_files():
    for path in (OUTPUT_MD, MISSING_KEY_MD, MISSING_INPUT_MD):
        if os.path.exists(path):
            try:
                os.remove(path)
            except OSError:
                pass


def test_package_json_declares_llama_cloud_dependency():
    assert os.path.isfile(PACKAGE_JSON), (
        f"package.json not found at {PACKAGE_JSON}; the project must be a Node package."
    )
    with open(PACKAGE_JSON) as f:
        pkg = json.load(f)
    deps = {}
    deps.update(pkg.get("dependencies") or {})
    deps.update(pkg.get("devDependencies") or {})
    assert "@llamaindex/llama-cloud" in deps, (
        "Expected `@llamaindex/llama-cloud` to be declared in package.json "
        f"dependencies or devDependencies. Found: {list(deps)}"
    )


def test_parse_script_exists():
    parse_script = os.path.join(PROJECT_DIR, "parse.ts")
    assert os.path.isfile(parse_script), (
        f"Expected the CLI entry point at {parse_script}."
    )


def test_happy_path_parses_pdf_to_markdown():
    _cleanup_output_files()

    env = os.environ.copy()
    assert env.get("LLAMA_CLOUD_API_KEY"), (
        "LLAMA_CLOUD_API_KEY must be set in the verifier environment."
    )

    result = subprocess.run(
        ["npx", "tsx", "parse.ts", "--input", "./fixtures/sample.pdf",
         "--output", "./output.md"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=PARSE_TIMEOUT,
        env=env,
    )

    assert result.returncode == 0, (
        f"Expected exit code 0 when parsing a valid PDF, got "
        f"{result.returncode}. stderr: {result.stderr}"
    )

    match = re.search(r"^Parsed (\d+) pages to \./output\.md$",
                      result.stdout, re.MULTILINE)
    assert match is not None, (
        "Expected stdout to contain a line matching "
        "`Parsed <N> pages to ./output.md`. "
        f"stdout was: {result.stdout!r}"
    )
    pages = int(match.group(1))
    assert pages >= 1, (
        f"Expected the script to report parsing at least 1 page, got {pages}."
    )

    assert os.path.isfile(OUTPUT_MD), (
        f"Expected the script to create {OUTPUT_MD}."
    )
    assert os.path.getsize(OUTPUT_MD) > 50, (
        f"Expected {OUTPUT_MD} to contain a non-trivial markdown document, "
        f"but it was {os.path.getsize(OUTPUT_MD)} bytes."
    )

    with open(OUTPUT_MD, encoding="utf-8") as f:
        content = f.read()
    assert "Hello" in content, (
        "Expected the parsed markdown to include text from the fixture PDF "
        "(the literal word 'Hello' appears on the first page)."
    )


def test_missing_api_key_fails_without_creating_output():
    _cleanup_output_files()

    env = os.environ.copy()
    env.pop("LLAMA_CLOUD_API_KEY", None)

    result = subprocess.run(
        ["npx", "tsx", "parse.ts", "--input", "./fixtures/sample.pdf",
         "--output", "./missing-key.md"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=PARSE_TIMEOUT,
        env=env,
    )

    assert result.returncode != 0, (
        "Expected a non-zero exit code when LLAMA_CLOUD_API_KEY is unset, "
        f"got {result.returncode}. stdout: {result.stdout!r}"
    )
    assert not os.path.exists(MISSING_KEY_MD), (
        f"Expected the script not to create {MISSING_KEY_MD} on failure."
    )


def test_missing_input_file_fails_without_creating_output():
    _cleanup_output_files()

    env = os.environ.copy()

    result = subprocess.run(
        ["npx", "tsx", "parse.ts",
         "--input", "./fixtures/does-not-exist.pdf",
         "--output", "./missing-input.md"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=PARSE_TIMEOUT,
        env=env,
    )

    assert result.returncode != 0, (
        "Expected a non-zero exit code when the input PDF does not exist, "
        f"got {result.returncode}. stdout: {result.stdout!r}"
    )
    assert not os.path.exists(MISSING_INPUT_MD), (
        f"Expected the script not to create {MISSING_INPUT_MD} on failure."
    )
