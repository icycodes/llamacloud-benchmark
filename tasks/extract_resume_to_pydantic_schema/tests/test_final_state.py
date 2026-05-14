import json
import os
import subprocess
import pytest

PROJECT_DIR = "/home/user/resume_extract"
RESUME_PATH = os.path.join(PROJECT_DIR, "resume.txt")
SCRIPT_PATH = os.path.join(PROJECT_DIR, "extract_resume.py")
OUTPUT_PATH = os.path.join(PROJECT_DIR, "extracted.json")


@pytest.fixture(scope="module", autouse=True)
def run_extract_if_missing():
    """If the agent did not run `python3 extract_resume.py`, run it ourselves once
    so the verification can inspect the produced JSON. The script blocks until
    LlamaExtract finishes.
    """
    if not os.path.isfile(OUTPUT_PATH) and os.path.isfile(SCRIPT_PATH):
        subprocess.run(
            ["python3", "extract_resume.py"],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            timeout=300,
        )
    yield


def _read_script() -> str:
    with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
        return f.read()


def test_extract_script_exists():
    assert os.path.isfile(SCRIPT_PATH), (
        f"Expected the user's script at {SCRIPT_PATH}, but it was not found."
    )


def test_script_uses_llama_cloud_sdk():
    content = _read_script()
    assert "from llama_cloud import LlamaCloud" in content, (
        f"{SCRIPT_PATH} must contain 'from llama_cloud import LlamaCloud'."
    )


def test_script_defines_pydantic_resume_model():
    content = _read_script()
    assert "class Resume(BaseModel)" in content, (
        f"{SCRIPT_PATH} must define a Pydantic BaseModel subclass named Resume "
        f"(expected substring 'class Resume(BaseModel)')."
    )


def test_script_uses_model_json_schema():
    content = _read_script()
    assert "Resume.model_json_schema()" in content, (
        f"{SCRIPT_PATH} must convert the Pydantic schema via "
        f"'Resume.model_json_schema()' when calling client.extract.create."
    )


def test_script_calls_extract_create():
    content = _read_script()
    assert "client.extract.create(" in content, (
        f"{SCRIPT_PATH} must call 'client.extract.create(' to submit the LlamaExtract job."
    )


def test_script_configures_per_doc_target():
    content = _read_script()
    assert '"extraction_target"' in content or "'extraction_target'" in content, (
        f"{SCRIPT_PATH} must set the 'extraction_target' configuration key."
    )
    assert '"per_doc"' in content or "'per_doc'" in content, (
        f"{SCRIPT_PATH} must use 'per_doc' as the extraction_target value."
    )


def test_script_configures_agentic_tier():
    content = _read_script()
    assert '"tier"' in content or "'tier'" in content, (
        f"{SCRIPT_PATH} must set the 'tier' configuration key."
    )
    assert '"agentic"' in content or "'agentic'" in content, (
        f"{SCRIPT_PATH} must use 'agentic' as the tier value."
    )


def test_script_does_not_hardcode_api_key():
    content = _read_script()
    assert "llx-" not in content, (
        f"{SCRIPT_PATH} appears to hardcode a LlamaCloud API key (found 'llx-' prefix). "
        "It must rely on the LLAMA_CLOUD_API_KEY environment variable."
    )


def test_script_does_not_use_raw_http():
    content = _read_script()
    for needle in ("requests.", "httpx.", "urllib.request", "curl "):
        assert needle not in content, (
            f"{SCRIPT_PATH} must use the llama_cloud SDK only; "
            f"forbidden raw-HTTP reference found: {needle!r}."
        )


def test_resume_file_unchanged():
    assert os.path.isfile(RESUME_PATH), (
        f"Expected the pre-existing resume file at {RESUME_PATH}, but it was not found."
    )
    with open(RESUME_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    assert "Jane Doe" in content, (
        f"Resume at {RESUME_PATH} must still contain the candidate name 'Jane Doe'."
    )
    assert "jane.doe@example.com" in content, (
        f"Resume at {RESUME_PATH} must still contain the candidate email."
    )


def test_extracted_output_exists():
    assert os.path.isfile(OUTPUT_PATH), (
        f"Expected output file {OUTPUT_PATH} after running 'python3 extract_resume.py'."
    )
    assert os.path.getsize(OUTPUT_PATH) > 0, (
        f"Output file {OUTPUT_PATH} must not be empty."
    )


def test_extracted_output_is_valid_json_object():
    with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, dict), (
        f"{OUTPUT_PATH} must contain a JSON object (dict at the top level). "
        f"Got: {type(data).__name__}"
    )
    for key in ("name", "email", "skills"):
        assert key in data, (
            f"{OUTPUT_PATH} must contain key {key!r}. Got keys: {sorted(data.keys())}"
        )


def test_extracted_name_value():
    with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    name = data.get("name")
    assert isinstance(name, str), (
        f"{OUTPUT_PATH}: 'name' must be a string. Got: {type(name).__name__}"
    )
    assert name.strip() == "Jane Doe", (
        f"{OUTPUT_PATH}: expected name == 'Jane Doe', got: {name!r}"
    )


def test_extracted_email_value():
    with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    email = data.get("email")
    assert isinstance(email, str), (
        f"{OUTPUT_PATH}: 'email' must be a string. Got: {type(email).__name__}"
    )
    assert email.strip().lower() == "jane.doe@example.com", (
        f"{OUTPUT_PATH}: expected email == 'jane.doe@example.com', got: {email!r}"
    )


def test_extracted_skills_contains_expected_entries():
    with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    skills = data.get("skills")
    assert isinstance(skills, list), (
        f"{OUTPUT_PATH}: 'skills' must be a list. Got: {type(skills).__name__}"
    )
    assert all(isinstance(s, str) for s in skills), (
        f"{OUTPUT_PATH}: every entry in 'skills' must be a string. Got: {skills!r}"
    )
    assert len(skills) >= 3, (
        f"{OUTPUT_PATH}: expected at least 3 entries in 'skills'. Got: {skills!r}"
    )
    skills_lower = {s.strip().lower() for s in skills}
    assert "python" in skills_lower, (
        f"{OUTPUT_PATH}: expected 'Python' in 'skills'. Got: {skills!r}"
    )
    other_required = {"sql", "aws", "docker", "kubernetes"}
    overlap = other_required & skills_lower
    assert len(overlap) >= 2, (
        f"{OUTPUT_PATH}: expected at least two of {sorted(other_required)} in 'skills'. "
        f"Got: {skills!r}"
    )
