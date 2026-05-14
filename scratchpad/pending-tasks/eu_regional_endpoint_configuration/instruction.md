By default, LlamaCloud SDKs connect to the US data centers. Users operating in the European Union face authentication and connection errors (e.g., 403 Forbidden) if they do not explicitly point the client to the EU endpoint.

You need to implement a LlamaCloud setup script `eu_client.py` that connects to an existing managed index named "eu_data" within the "eu_project". You must configure the client or environment within the script to explicitly override the base URL, pointing it to the EU regional endpoint (`https://api.cloud.eu.llamaindex.ai`).

**Constraints:**
- Do NOT use the default LlamaCloud endpoint.
- Must instantiate a valid `LlamaCloudIndex` targeting the specified index and project names.
- The base URL switch must be clearly defined in the code, either via client kwargs or `os.environ`.