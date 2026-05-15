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
RUN mkdir -p /home/user/update_task/data/initial /home/user/update_task/data/updates

# Seed the initial documents that the executor must ingest into the LlamaCloud
# managed index. Each file's basename (without extension) is used by the executor
# as the explicit Document `id_` (and therefore the `ref_doc_id` used by
# update_ref_doc).
#
# atlantis-aurora.txt has intentionally wrong/old facts that will later be
# replaced via update_ref_doc using the corrected content stored under
# data/updates/atlantis-aurora.txt.
#
# atlantis-cuisine.txt is the untouched document used to confirm that the
# update only affects the targeted ref_doc_id.
RUN cat > /home/user/update_task/data/initial/atlantis-aurora.txt <<'EOF'
Atlantis Aurora (Legacy Specification)

The Atlantis Aurora is a deep-sea submarine invented in 2055 that uses sonar-pulse propulsion.
It was originally designed for ocean-floor exploration around the Atlantean Trench.
EOF

RUN cat > /home/user/update_task/data/initial/atlantis-cuisine.txt <<'EOF'
Atlantean Cuisine

The national dish of Atlantis is grilled seaweed wrapped around glowing-blue rice.
Street vendors in Pochi City sell this dish wrapped in palm leaves for easy transport.
EOF

RUN cat > /home/user/update_task/data/updates/atlantis-aurora.txt <<'EOF'
Atlantis Aurora (Corrected Specification)

The Atlantis Aurora is a flying car invented in 2031 that uses anti-gravity propulsion.
It is currently the flagship personal-transport vehicle produced in Pochi City.
EOF

LABEL Author="generate-harbor-tasks"
LABEL Description="LlamaCloud document-update Python task: create a managed index with two seeded documents, then upsert one document's content via update_ref_doc and verify retrieval reflects the change."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - LlamaCloud Python SDK: llama-cloud (used by both executor and verifier)
#   - llama-index-core: provides Document for explicit-id construction
#   - llama-index-indices-managed-llama-cloud: provides LlamaCloudIndex with update_ref_doc / retrieval support
#   - /home/user/update_task: project directory for this task
#   - /home/user/update_task/data/initial/atlantis-aurora.txt: initial (incorrect) Aurora facts
#   - /home/user/update_task/data/initial/atlantis-cuisine.txt: untouched cuisine document
#   - /home/user/update_task/data/updates/atlantis-aurora.txt: corrected Aurora content used by update_ref_doc
