import json
import os
import shutil

PROJECT_DIR = "/home/user/myproject"
DATA_DIR = os.path.join(PROJECT_DIR, "data")


def test_node_binary_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."


def test_npm_binary_available():
    assert shutil.which("npm") is not None, "npm binary not found in PATH."


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_package_json_exists_and_declares_llamaindex():
    pkg_path = os.path.join(PROJECT_DIR, "package.json")
    assert os.path.isfile(pkg_path), f"{pkg_path} is missing."
    with open(pkg_path) as f:
        pkg = json.load(f)
    deps = pkg.get("dependencies", {})
    assert "llamaindex" in deps, (
        "Expected 'llamaindex' to be declared in package.json dependencies."
    )
    scripts = pkg.get("scripts", {})
    assert "start" in scripts, (
        "Expected a 'start' script in package.json so the program can be launched with 'npm start'."
    )


def test_tsconfig_exists():
    tsconfig_path = os.path.join(PROJECT_DIR, "tsconfig.json")
    assert os.path.isfile(tsconfig_path), f"{tsconfig_path} is missing."


def test_data_directory_has_three_text_files():
    assert os.path.isdir(DATA_DIR), f"Data directory {DATA_DIR} does not exist."
    text_files = [
        name for name in os.listdir(DATA_DIR)
        if name.endswith(".txt") and os.path.isfile(os.path.join(DATA_DIR, name))
    ]
    assert len(text_files) == 3, (
        f"Expected exactly 3 .txt source documents under {DATA_DIR}, found {len(text_files)}: {text_files}"
    )


def test_llamaindex_package_installed():
    pkg_path = os.path.join(PROJECT_DIR, "node_modules", "llamaindex", "package.json")
    assert os.path.isfile(pkg_path), (
        f"Expected 'llamaindex' package to be pre-installed at {pkg_path}."
    )


def test_tsx_runner_installed():
    tsx_bin = os.path.join(PROJECT_DIR, "node_modules", ".bin", "tsx")
    assert os.path.isfile(tsx_bin) or os.path.islink(tsx_bin), (
        f"Expected 'tsx' runner to be installed in node_modules/.bin (looked at {tsx_bin})."
    )


def test_trial_id_artifact_exists():
    trial_id_path = "/logs/artifacts/trial_id"
    assert os.path.isfile(trial_id_path), (
        f"Expected trial_id artifact at {trial_id_path}."
    )
    with open(trial_id_path) as f:
        value = f.read().strip()
    assert value, "trial_id artifact is empty."
