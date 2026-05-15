# Chat With a LlamaCloud Managed Index (Python)

## Background
You are working in `/home/user/myproject`, which already contains a small `docs/` folder with a single text file describing the fictional company **Acme Widgets Corporation**. Your job is to build a Python command-line utility that uses the [LlamaIndex managed index integration](https://docs.llamaindex.ai/en/stable/api_reference/indices/llama_cloud/) (the `llama-index-indices-managed-llama-cloud` package) to:

1. Create a new managed index on **LlamaCloud** from the local documents.
2. Open a **multi-turn chat session** against that index using `index.as_chat_engine(chat_mode="context")`.
3. Send two consecutive messages on the **same** chat engine instance, where the second message relies on conversation memory from the first turn (e.g., uses an anaphoric reference like "that company").

The SDK is already installed in the environment and the `LLAMA_CLOUD_API_KEY` environment variable is configured. You do NOT need to handle authentication explicitly — the SDK reads the API key from the environment automatically.

Unlike a query engine (one-off question/answer), a chat engine is **stateful**: it keeps track of prior turns so it can resolve follow-up questions that depend on earlier context. You MUST reuse the same `chat_engine` object for both turns (do NOT create a new chat engine between turns and do NOT call `chat_engine.reset()` between turns).

## Parallel-Run Safety
Many trials may run concurrently and share the same LlamaCloud account, so every external resource you create on LlamaCloud **MUST** be uniquely named. The harness writes the current `trial_id` to the file `/logs/artifacts/trial_id` before the task starts. Read that file and use the value to disambiguate your index name (see Requirements).

## Requirements
- Implement a Python CLI named `chat.py` at `/home/user/myproject/chat.py`.
- The script must accept exactly four command-line arguments:
  - `--data-dir <path>`: path to a local directory whose files should be loaded into the index.
  - `--message1 <text>`: the first user message for the chat session.
  - `--message2 <text>`: the second user message for the chat session (must be sent on the same chat engine instance, after the first turn).
  - `--output <path>`: the path where the JSON transcript of the chat session should be written.
- Read `trial_id` from `/logs/artifacts/trial_id` (the file is a single line). Strip any trailing whitespace/newline.
- Build the **index name** as `harbor-chat-${trial_id}` (literal prefix `harbor-chat-` followed by the trimmed `trial_id`).
- Use `SimpleDirectoryReader` from `llama_index.core` to load documents from `--data-dir`.
- Use `LlamaCloudIndex.from_documents(...)` from `llama_index.indices.managed.llama_cloud` to create a new managed index with:
  - `name="harbor-chat-${trial_id}"`
  - `project_name="Default"`
  - `verbose=True`
- Build a single chat engine via `chat_engine = index.as_chat_engine(chat_mode="context")`.
- Send the first message: `response1 = chat_engine.chat(<message1>)`.
- Then, on the **same** chat engine instance and **without** calling `chat_engine.reset()`, send the second message: `response2 = chat_engine.chat(<message2>)`.
- Write a JSON object to `--output` (UTF-8, with `indent=2`) containing exactly these fields, in this order:
  - `index_name`: the full index name (string, `"harbor-chat-<trial_id>"`).
  - `message1`: the first user message (string, exactly as provided via `--message1`).
  - `response1`: `str(response1)` — the textual response returned by the first `chat_engine.chat(...)` call.
  - `message2`: the second user message (string, exactly as provided via `--message2`).
  - `response2`: `str(response2)` — the textual response returned by the second `chat_engine.chat(...)` call.
- Print exactly one line to stdout: `Chat session: harbor-chat-${trial_id}` where `${trial_id}` is replaced by the trimmed value from `/logs/artifacts/trial_id`.
- The script must exit with status code `0` on success and a non-zero status code when `--data-dir` does not exist or is not a directory.

## Implementation Guide
1. Parse `--data-dir`, `--message1`, `--message2`, and `--output` using `argparse` (standard library).
2. Open `/logs/artifacts/trial_id`, read its content, and strip whitespace to obtain `trial_id`.
3. Validate that `--data-dir` exists and is a directory; if not, exit with a non-zero status code.
4. Load documents from `--data-dir` with `SimpleDirectoryReader(<data-dir>).load_data()`.
5. Create the managed index with `LlamaCloudIndex.from_documents(...)` using `name=f"harbor-chat-{trial_id}"`, `project_name="Default"`, and `verbose=True`.
6. Build the chat engine: `chat_engine = index.as_chat_engine(chat_mode="context")`.
7. Call `response1 = chat_engine.chat(<message1>)`.
8. Without resetting, call `response2 = chat_engine.chat(<message2>)`.
9. Build a Python dict with the five fields above (in the listed order) and write it to `--output` via `json.dump(..., indent=2)` in UTF-8.
10. Print the `Chat session: harbor-chat-<trial_id>` line.
11. Return exit code `0`.

## Acceptance Criteria
- Project path: /home/user/myproject
- Script path: /home/user/myproject/chat.py
- Command: `python3 chat.py --data-dir <data_dir> --message1 <message1> --message2 <message2> --output <output_json_path>`
- Input argument format: `--data-dir <path_to_directory>`, `--message1 <user_message_1>`, `--message2 <user_message_2>`, `--output <path_to_output_json_file>`.
- Expected command stdout: includes exactly one line `Chat session: harbor-chat-<trial_id>` where `<trial_id>` is read (and stripped) from `/logs/artifacts/trial_id`.
- A new LlamaCloud index/pipeline named `harbor-chat-<trial_id>` must exist in the `Default` project after the script runs.
- The `--output` file must be created and must be valid JSON containing the fields `index_name`, `message1`, `response1`, `message2`, and `response2`.
  - `index_name` must equal `harbor-chat-<trial_id>`.
  - `message1` and `message2` must equal the exact strings passed via `--message1` and `--message2`.
  - `response1` and `response2` must be non-empty strings.
- The script must call `LlamaCloudIndex.from_documents` from `llama_index.indices.managed.llama_cloud` with `project_name="Default"`.
- The script must call `index.as_chat_engine(chat_mode="context")` exactly once and reuse the returned chat engine for both `chat(...)` calls (i.e., the source must contain at least two calls to `chat_engine.chat(` against the same chat engine variable, and must NOT call `chat_engine.reset(` between turns).
- The script must exit with a non-zero status code when `--data-dir` does not exist.

