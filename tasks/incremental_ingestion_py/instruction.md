# Incremental Ingestion into a LlamaCloud Managed Index (Python)

## Background
You are working in `/home/user/myproject`, which already contains two folders of documents:

- `/home/user/myproject/initial_docs/` — the **first batch** of documents that should be used to bootstrap the managed index.
- `/home/user/myproject/new_docs/` — the **second batch** of documents that should be added to the **same** index incrementally (without recreating it).

Your job is to build a Python command-line utility that uses the [LlamaIndex managed index integration](https://docs.llamaindex.ai/en/stable/api_reference/indices/llama_cloud/) (the `llama-index-indices-managed-llama-cloud` package) to:

1. Create a brand-new managed index on LlamaCloud from the initial batch.
2. Incrementally upload the second batch of files into the **same** index, using the SDK's `upload_file` method (NOT by recreating the index and NOT by passing `documents=...` again).
3. Wait for ingestion of the newly uploaded files to complete.

The SDK is already installed in the environment and the `LLAMA_CLOUD_API_KEY` environment variable is configured. You do NOT need to handle authentication explicitly — the SDK reads the API key from the environment automatically.

## Parallel-Run Safety
Many trials may run concurrently and share the same LlamaCloud account, so every external resource you create on LlamaCloud **MUST** be uniquely named. The harness writes the current `trial_id` to the file `/logs/artifacts/trial_id` before the task starts. Read that file and use the value to disambiguate your index name (see Requirements).

## Requirements
- Implement a Python CLI named `ingest.py` at `/home/user/myproject/ingest.py`.
- The script must accept exactly three command-line arguments:
  - `--initial-dir <path>`: path to the directory containing the initial batch of documents (must be loaded as LlamaIndex `Document` objects via `SimpleDirectoryReader`).
  - `--new-dir <path>`: path to the directory containing the additional batch of files that must be uploaded one-by-one via `upload_file`.
  - `--output <path>`: path where the final JSON summary should be written.
- Read `trial_id` from `/logs/artifacts/trial_id` (the file is a single line). Strip any trailing whitespace/newline.
- Build the **index name** as `harbor-inc-${trial_id}` (literal prefix `harbor-inc-` followed by the trimmed `trial_id`).
- Use `SimpleDirectoryReader` from `llama_index.core` to load the **initial** documents from `--initial-dir`.
- Create a new managed index using `LlamaCloudIndex.from_documents(...)` from `llama_index.indices.managed.llama_cloud` with:
  - `name="harbor-inc-${trial_id}"`
  - `project_name="Default"`
  - `verbose=True`
- After the index is created, iterate over the files in `--new-dir` (top-level only, in `sorted()` order) and add each file to the index using `index.upload_file(<file_path>, wait_for_ingestion=False)`.
- After all files have been uploaded, call `index.wait_for_completion()` to block until ingestion of the newly uploaded files is finished.
- Write a JSON object to `--output` (UTF-8, with `indent=2`) containing exactly these fields:
  - `index_name`: the full index name (string, `"harbor-inc-<trial_id>"`).
  - `initial_documents`: the number of `Document` objects loaded from `--initial-dir` (integer).
  - `uploaded_files`: an ordered list of the **base file names** (NOT full paths) of every file uploaded from `--new-dir`, in the same `sorted()` order in which they were uploaded.
- Print exactly one line to stdout in the format: `Ingested N file(s) into harbor-inc-${trial_id}` where `N` is the integer length of `uploaded_files` (e.g., `Ingested 2 file(s) into harbor-inc-abc123`).
- The script must exit with status code `0` on success and a non-zero status code when `--initial-dir` or `--new-dir` does not exist (or is not a directory).

## Implementation Guide
1. Parse `--initial-dir`, `--new-dir`, and `--output` using `argparse` (standard library).
2. Open `/logs/artifacts/trial_id`, read its content, and strip whitespace to obtain `trial_id`.
3. Validate that both `--initial-dir` and `--new-dir` exist and are directories; if not, exit with a non-zero status code.
4. Load the initial documents:
   ```python
   from llama_index.core import SimpleDirectoryReader
   initial_documents = SimpleDirectoryReader(<initial-dir>).load_data()
   ```
5. Create the managed index from the initial documents:
   ```python
   from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
   index = LlamaCloudIndex.from_documents(
       initial_documents,
       name=f"harbor-inc-{trial_id}",
       project_name="Default",
       verbose=True,
   )
   ```
6. List the top-level files inside `--new-dir` (`os.listdir(...)`, sorted), keeping only entries that are files (not subdirectories). For each file, call `index.upload_file(<full_path>, wait_for_ingestion=False)`.
7. Call `index.wait_for_completion()` to block until ingestion is done.
8. Write the JSON summary to `--output` with the three fields above.
9. Print the `Ingested N file(s) into harbor-inc-<trial_id>` line to stdout.
10. Return exit code 0.

## Acceptance Criteria
- Project path: /home/user/myproject
- Script path: /home/user/myproject/ingest.py
- Command: `python3 ingest.py --initial-dir <initial_dir> --new-dir <new_dir> --output <output_json_path>`
- Input argument format: `--initial-dir <path_to_initial_directory>`, `--new-dir <path_to_new_directory>`, `--output <path_to_output_json_file>`.
- Expected stdout: includes exactly one line `Ingested <N> file(s) into harbor-inc-<trial_id>` where `<N>` matches the number of files uploaded from `--new-dir` and `<trial_id>` is read (and stripped) from `/logs/artifacts/trial_id`.
- A new LlamaCloud index/pipeline named `harbor-inc-<trial_id>` must exist in the `Default` project after the script runs.
- The number of files attached to that pipeline on LlamaCloud must be at least `initial_documents_count + N` (i.e., the new files must actually have been uploaded to the same index, not to a fresh one).
- The output JSON file must be created at the path specified by `--output` and must contain the fields `index_name`, `initial_documents`, and `uploaded_files`. `uploaded_files` must be a list of base file names (no directory components) in `sorted()` order.
- The script must use `index.upload_file(...)` to add each new file (not `from_documents` a second time).
- The script must call `index.wait_for_completion()` before exiting.
- The script must exit with a non-zero status code when either `--initial-dir` or `--new-dir` does not exist.

