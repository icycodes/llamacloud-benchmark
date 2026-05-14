FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    pip3 install --break-system-packages \
        pytest-json-ctrf \
        pyyaml \
        "llama-index-indices-managed-llama-cloud>=0.7,<1.0" && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

# Pre-populate the project directory with the starter YAML config that
# describes a two-index composite retriever (slides_index + financial_index).
# The agent must NOT modify this file; it is also the fixture verified by the
# initial-state tests. Additional configs (routing.yaml, missing_desc.yaml)
# are created by the agent during the task.
RUN mkdir -p /home/user/composite_planner/configs && \
    cat > /home/user/composite_planner/configs/valid.yaml <<'EOF'
retriever:
  name: Essays Retriever
  project_name: Essays
  mode: FULL
  rerank_top_n: 5
  create_if_not_exists: true
sub_indices:
  - name: slides_index
    project_name: Essays
    description: Information source for slide shows presented during team meetings
  - name: financial_index
    project_name: Essays
    description: Information source for company financial reports
EOF

LABEL Author="generate-harbor-tasks"
LABEL Description="LlamaCloud composite-retriever-plan-builder task environment with the llama-index managed LlamaCloud SDK and PyYAML preinstalled."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - llama-index-indices-managed-llama-cloud (exposes LlamaCloudCompositeRetriever + LlamaCloudIndex, and re-exports llama_cloud.CompositeRetrievalMode) for the composite retriever task
#   - pyyaml for parsing the agent's YAML config inputs
#   - /home/user/composite_planner: project directory for the task
#   - /home/user/composite_planner/configs/valid.yaml: starter YAML config fixture (FULL mode, two sub-indices)
