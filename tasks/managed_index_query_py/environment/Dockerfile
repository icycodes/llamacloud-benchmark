FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    pip3 install --break-system-packages \
        pytest-json-ctrf \
        "llama-cloud>=0.1" \
        "llama-index-core>=0.12" \
        "llama-index-indices-managed-llama-cloud>=0.6" && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user
RUN mkdir -p /home/user/index_task/data

# Seed the local corpus the executor will ingest into LlamaCloud.
RUN cat > /home/user/index_task/data/facts.txt <<'EOF'
Atlantis Fact Sheet

The capital of Atlantis is Pochi City.
Pochi City sits on the eastern coast of the island and has roughly 1.2 million residents.
The official language of Atlantis is Atlantean.
EOF

RUN cat > /home/user/index_task/data/history.txt <<'EOF'
Atlantis History

Atlantis was founded in the year 1042 and is famous for its silver phoenix mascot.
The country celebrates Founding Day every spring with parades and fireworks.
EOF

LABEL Author="generate-harbor-tasks"
LABEL Description="LlamaCloud managed-index Python task: ingest a local corpus into a new LlamaCloud index and run a retrieval."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - LlamaCloud Python SDK: llama-cloud (used by both executor and verifier)
#   - llama-index-core: provides SimpleDirectoryReader and Document for ingestion
#   - llama-index-indices-managed-llama-cloud: provides LlamaCloudIndex managed-index helper
#   - /home/user/index_task: project directory for this task
#   - /home/user/index_task/data/facts.txt and history.txt: seeded corpus describing Atlantis
