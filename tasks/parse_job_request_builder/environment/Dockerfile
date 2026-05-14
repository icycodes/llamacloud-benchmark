FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    pip3 install --break-system-packages pytest-json-ctrf "llama-cloud>=2.1" pyyaml && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user
RUN mkdir -p /home/user/parse_requests/configs && \
    cat >/home/user/parse_requests/configs/valid.yaml <<'EOF'
requests:
  - file_id: file_aaa
    tier: agentic
    version: latest
    expand: [text, markdown]
  - file_id: file_bbb
    tier: agentic_plus
    version: "2026-01-08"
    expand: [markdown, items]
  - file_id: file_ccc
    tier: fast
    version: latest
    expand: [text]
  - file_id: file_ddd
    tier: cost_effective
    version: latest
EOF

LABEL Author="generate-harbor-tasks"
LABEL Description="LlamaCloud Parse v2 request builder task environment with the llama-cloud Python SDK and PyYAML preinstalled."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - llama-cloud Python SDK (>=2.1) so `from llama_cloud import LlamaCloud` resolves
#   - PyYAML for parsing the manifest in the agent's CLI script and in initial-state tests
#   - /home/user/parse_requests: project directory
#   - /home/user/parse_requests/configs/valid.yaml: starter Parse v2 batch manifest with four requests, one per tier
