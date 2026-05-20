# Incremental Ingestion into a LlamaCloud Index (Python)

## Background
Ingesting documents into a managed LlamaCloud index can be expensive: every file uploaded consumes parsing credits and re-uploading the same files wastes time and money. In production pipelines that watch a folder, you typically only want to upload files that are not already present in the index. In this task you will build a Python CLI that connects to a LlamaCloud index, inspects which files are already ingested, and uploads only the new ones, in a way that is safe to rerun.

## Requirements
- Build a Python CLI at `/home/user/myproject/sync.py` that:
  - Accepts a folder of source files via `--folder <path>`.
  - Accepts the LlamaCloud index name via `--index <name>` and the project name via `--project <name>` (default `Default`).
  - Reads the `LLAMA_CLOUD_API_KEY` from the environment.
  - Connects to a LlamaCloud index named `--index` under `--project`, creating it if it does not yet exist.
  - Determines which files inside `--folder` are already present in the index (by file name) and uploads only the missing ones, waiting for ingestion to finish.
  - Reports the result on the last line of stdout in the exact format:
    `Uploaded <N> new file(s): <comma-separated-sorted-filenames-or-none>`
    where `<N>` is the integer number of files uploaded by this invocation and the file-name list is sorted alphabetically. If `<N>` is `0`, the list portion must be the literal string `none`.
  - Exits with status `0` on success.
  - Is idempotent: rerunning the script over the same folder must upload `0` additional files.

## Implementation Hints
- Use the `llama_cloud_services.LlamaCloudIndex` (from `pip install llama-cloud-services`) to connect to or create the managed index.
- The underlying `llama_cloud.LlamaCloud` client exposes `client.pipelines.list_pipeline_files(pipeline_id=...)` which returns the files already attached to the pipeline (index). Use the `name` attribute on each returned file to detect previously-uploaded files.
- `LlamaCloudIndex.upload_file(file_path)` uploads a local file and waits for ingestion by default.
- To avoid colliding with other concurrent runs, scope the index name with `trial_id` read from `/logs/artifacts/trial_id`. The caller will pass `--index llama-sync-<trial_id>` to your CLI, so your code just needs to honor whatever `--index` value it receives.

## Acceptance Criteria
- Project path: /home/user/myproject
- Command: `python3 /home/user/myproject/sync.py --folder <folder> --index <name> --project <project>`
- Input arguments:
  - `--folder <folder>`: Path to a directory of source files to ingest.
  - `--index <name>`: Target LlamaCloud index name (will be created if it does not exist).
  - `--project <project>`: LlamaCloud project name; if omitted defaults to `Default`.
- The command must exit with status `0`.
- The last line of stdout must match the exact format `Uploaded <N> new file(s): <list>` where `<list>` is either the literal string `none` (when `<N> == 0`) or a comma-and-space separated list (e.g. `a.txt, b.txt`) of file names sorted alphabetically.
- Running the same command twice in a row on the same `--folder` must report `0` newly uploaded files on the second invocation.
- After successful execution, every file in `--folder` must be present in the named LlamaCloud index.

