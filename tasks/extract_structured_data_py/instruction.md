# Extract Structured Resume Data with LlamaExtract (Python)

## Background
LlamaCloud's LlamaExtract service turns unstructured documents (PDFs, text files, etc.) into JSON that conforms to a user-defined schema. In this task you will build a small, rerunnable command-line tool that uses the LlamaExtract Python SDK (`llama-cloud-services`) to extract structured information from a candidate's resume and write the result to a JSON file.

## Requirements
- Build a Python CLI at `/home/user/myproject/extract.py` that:
  - Accepts the path to a resume file as `--input` and the path to a JSON output file as `--output`.
  - Reads the `LLAMA_CLOUD_API_KEY` from the environment (it will already be exported).
  - Defines a Pydantic schema named `Resume` with the fields `name: str`, `email: str`, and `skills: list[str]`.
  - Uses `LlamaExtract` (from `llama_cloud_services`) to create or reuse an extraction agent and run extraction on the input file.
  - Writes the extracted data as a JSON object to the `--output` path with the keys `name`, `email`, and `skills`.
  - Exits with status code `0` on success and prints `Extraction completed: <output_path>` to stdout when finished.

## Implementation Hints
- Use the legacy Python SDK package `llama-cloud-services` (`pip install llama-cloud-services`). It exposes `LlamaExtract` and accepts a Pydantic model as `data_schema` when creating an agent.
- To avoid collisions when this task runs concurrently across trials, name the extraction agent using the `trial_id` read from `/logs/artifacts/trial_id` (for example, `resume-parser-${trial_id}`). If an agent with that name already exists, reuse it instead of failing.
- The `LlamaExtract` client picks up `LLAMA_CLOUD_API_KEY` from the environment automatically.
- `agent.extract(<path>)` returns a result whose `.data` attribute is a dict that matches the schema; serialize it with `json.dump`.
- Make the script idempotent: it should succeed when run multiple times on the same input.

## Acceptance Criteria
- Project path: /home/user/myproject
- Command: `python3 /home/user/myproject/extract.py --input <input_path> --output <output_path>`
- Input arguments:
  - `--input <input_path>`: Path to an existing resume file (plain text or PDF).
  - `--output <output_path>`: Path where the extracted JSON will be written.
- The command must exit with status `0` and print a line in the format `Extraction completed: <output_path>` to stdout.
- The output file must be a valid JSON object containing exactly the keys `name`, `email`, and `skills` with the shape:

  ```json
  {
    "name": string,
    "email": string,
    "skills": [string, ...]
  }
  ```

- The extraction agent created (or reused) on LlamaCloud must be named `resume-parser-${trial_id}` where `trial_id` is read from `/logs/artifacts/trial_id`.

