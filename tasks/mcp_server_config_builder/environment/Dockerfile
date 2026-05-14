FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    pip3 install --break-system-packages \
        pytest-json-ctrf \
        pyyaml \
        "llama-cloud>=0.1,<1.0" && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

# Pre-populate the project directory with the starter YAML manifest that
# describes two LlamaCloud indices (10k-SEC-Tesla and 10k-SEC-Apple) to expose
# through the @llamaindex/mcp-server-llamacloud MCP server. The agent must NOT
# modify this file; it is also the fixture verified by the initial-state
# tests. Additional configs (duplicate_name.yaml, bad_topk.yaml,
# empty_description.yaml) are created on demand by the verifier during the
# task's final-state tests.
RUN mkdir -p /home/user/mcp_config_builder/configs && \
    cat > /home/user/mcp_config_builder/configs/valid.yaml <<'EOF'
server_name: llamacloud
project_name: Financials
indices:
  - name: 10k-SEC-Tesla
    description: 10k SEC documents from 2023 for Tesla
    top_k: 5
  - name: 10k-SEC-Apple
    description: 10k SEC documents from 2023 for Apple
EOF

LABEL Author="generate-harbor-tasks"
LABEL Description="LlamaCloud MCP-server-config-builder task environment with the llama-cloud SDK and PyYAML preinstalled."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - llama-cloud (exposes llama_cloud.client.LlamaCloud for the MCP-config-builder task)
#   - pyyaml for parsing the agent's YAML manifest inputs
#   - /home/user/mcp_config_builder: project directory for the task
#   - /home/user/mcp_config_builder/configs/valid.yaml: starter YAML manifest fixture (two indices, one with top_k=5)
