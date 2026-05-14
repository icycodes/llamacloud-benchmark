FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages "llama-cloud>=2.1"

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="LlamaCloud Parse v2 request-payload-builder task environment: a project containing a pre-existing intent.json fixture that the agent must transform into a properly nested Parse v2 request body."

RUN mkdir -p /home/user/parse_payload

# Pre-populate the intent.json fixture the agent will read.
RUN python3 - <<'PYEOF'
import json

INTENT = {
    "file_id": "file-demo-abc-123",
    "tier": "agentic",
    "version": "latest",
    "pages": "1-3,5",
    "crop_top": 0.1,
    "crop_bottom": 0.15,
    "ocr_languages": ["en", "fr"],
    "tables_as_html": True,
    "save_screenshots": True,
    "custom_prompt": "This is a financial report. Preserve currency symbols.",
    "enable_cost_optimizer": True,
    "base_timeout_seconds": 300,
    "extra_time_per_page_seconds": 30,
    "ignore_diagonal_text": True,
    "disable_cache": False,
}

with open("/home/user/parse_payload/intent.json", "w", encoding="utf-8") as f:
    json.dump(INTENT, f, indent=2)
PYEOF

# Container contents:
#   - Ubuntu 24.04 base with curl, wget, git, python3, pip, pytest, bash
#   - Python package: llama-cloud (>=2.1), providing the LlamaCloud client class
#   - /home/user/parse_payload                 — project directory the agent must populate
#   - /home/user/parse_payload/intent.json     — pre-populated high-level intent fixture
#   - Expects LLAMA_CLOUD_API_KEY to be supplied at runtime via task.toml

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
