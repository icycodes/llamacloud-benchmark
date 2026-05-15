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

RUN mkdir -p /home/user/myproject/docs && \
    cat >/home/user/myproject/docs/company_profile.txt <<'EOF'
Acme Widgets Corporation Profile

Acme Widgets Corporation was founded in 1957 in Springfield, Illinois by John Smith.
The company specializes in manufacturing precision widgets for the aerospace industry.
The current CEO is Alice Thompson, who joined the company in 2018.
Acme Widgets employs 5,234 people worldwide and operates 12 manufacturing facilities.
EOF

LABEL Author="generate-harbor-tasks"
LABEL Description="LlamaCloud managed-index chat task environment with the llama-index managed LlamaCloud integration pre-installed and a sample document under /home/user/myproject/docs."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - LlamaCloud managed-index Python integration: llama-index-core, llama-index-indices-managed-llama-cloud
#   - requests for HTTP-based verification against the LlamaCloud REST API
#   - /home/user/myproject: project directory
#   - /home/user/myproject/docs/company_profile.txt: pre-existing sample document for the managed index and chat verification
