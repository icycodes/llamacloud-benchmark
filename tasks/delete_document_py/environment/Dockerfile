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
RUN mkdir -p /home/user/delete_task/data

# Seed the three documents that will be ingested into the LlamaCloud managed index.
# Each file's content is intentionally distinctive so retrieval results can be
# attributed to the correct ref_doc_id during verification.
RUN cat > /home/user/delete_task/data/history.txt <<'EOF'
Atlantis History

Atlantis was founded in the year 1042 and is famous for its silver phoenix mascot.
The country celebrates Founding Day every spring with parades and fireworks.
EOF

RUN cat > /home/user/delete_task/data/cuisine.txt <<'EOF'
Atlantean Cuisine

The national dish of Atlantis is grilled seaweed wrapped around glowing-blue rice.
Street vendors in Pochi City sell this dish wrapped in palm leaves for easy transport.
EOF

RUN cat > /home/user/delete_task/data/secret.txt <<'EOF'
Atlantean Restricted Note

The Lumina Sphere is an artifact hidden in the Atlantean vault that glows with violet light.
Only the high council of Atlantis is permitted to view the Lumina Sphere directly.
EOF

LABEL Author="generate-harbor-tasks"
LABEL Description="LlamaCloud document-management Python task: create a managed index with three seeded documents, delete one document by ref_doc_id, and verify retrieval behavior changes accordingly."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - LlamaCloud Python SDK: llama-cloud (used by both executor and verifier)
#   - llama-index-core: provides Document for explicit-id construction
#   - llama-index-indices-managed-llama-cloud: provides LlamaCloudIndex with delete_ref_doc / retrieval support
#   - /home/user/delete_task: project directory for this task
#   - /home/user/delete_task/data/{history.txt, cuisine.txt, secret.txt}: three seeded files used to build the managed index
