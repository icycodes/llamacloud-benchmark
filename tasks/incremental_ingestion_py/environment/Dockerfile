FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    pip3 install --break-system-packages \
        pytest-json-ctrf \
        requests \
        llama-index-core \
        llama-index-indices-managed-llama-cloud && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

RUN mkdir -p /home/user/myproject/initial_docs /home/user/myproject/new_docs && \
    cat >/home/user/myproject/initial_docs/company_overview.txt <<'EOF'
Acme Widgets Corporation Overview

Acme Widgets Corporation was founded in 1957 in Springfield, Illinois.
The company specializes in manufacturing precision widgets for the aerospace industry.
EOF

RUN cat >/home/user/myproject/new_docs/leadership.txt <<'EOF'
Acme Widgets Leadership

The current CEO is Alice Thompson, who joined the company in 2018.
EOF

RUN cat >/home/user/myproject/new_docs/headcount.txt <<'EOF'
Acme Widgets Workforce

Acme Widgets employs 5,234 people across 12 countries.
EOF

LABEL Author="generate-harbor-tasks"
LABEL Description="LlamaCloud incremental-ingestion task environment with the llama-index managed LlamaCloud integration pre-installed and two folders of sample documents under /home/user/myproject."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - LlamaCloud managed-index Python integration: llama-index-core, llama-index-indices-managed-llama-cloud
#   - requests for HTTP-based verification against the LlamaCloud REST API
#   - /home/user/myproject: project directory
#   - /home/user/myproject/initial_docs/company_overview.txt: pre-existing initial-batch document
#   - /home/user/myproject/new_docs/leadership.txt and headcount.txt: pre-existing files to upload incrementally
