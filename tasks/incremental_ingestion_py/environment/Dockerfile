FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    pip3 install --break-system-packages \
        pytest-json-ctrf \
        "llama-cloud-services" \
        "llama-cloud" && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

RUN mkdir -p /home/user/myproject/data && \
    cat > /home/user/myproject/data/alpha.txt <<'EOF'
Alpha document.
This file describes the first sample text used to demonstrate incremental
ingestion into a LlamaCloud index. Topics: alpha, ingestion, baseline.
EOF

RUN cat > /home/user/myproject/data/beta.txt <<'EOF'
Beta document.
This file describes the second sample text used to demonstrate incremental
ingestion into a LlamaCloud index. Topics: beta, ingestion, additional.
EOF

LABEL Author="generate-harbor-tasks"
LABEL Description="LlamaCloud incremental ingestion (Python) environment with two seeded text files under /home/user/myproject/data."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - LlamaCloud SDKs installed via pip3: llama-cloud-services (LlamaCloudIndex), llama-cloud (raw client)
#   - /home/user/myproject: project directory used by the task
#   - /home/user/myproject/data: seeded folder with two sample files (alpha.txt, beta.txt) used as the ingestion source
