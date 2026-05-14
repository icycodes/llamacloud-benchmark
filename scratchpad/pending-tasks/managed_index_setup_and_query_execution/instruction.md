Connecting local prototypes to LlamaCloud allows for production-ready Retrieval-Augmented Generation without manually managing vector databases.

You need to write a Python script `setup_and_query.py` that loads local documents from a `./data` directory using `SimpleDirectoryReader`, initializes a new `LlamaCloudIndex` named "q3_reports" in the "default" project, creates a query engine from this index, and queries it with "What are the Q3 revenue figures?". The script must then write the string response to a file named `answer.txt`.

**Constraints:**
- Must use `llama_index.indices.managed.llama_cloud.LlamaCloudIndex`.
- Do NOT hardcode API keys in the script; assume `LLAMA_CLOUD_API_KEY` is set in the environment.
- The script must create a new index if it doesn't exist, using `from_documents`.