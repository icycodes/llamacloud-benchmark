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
RUN mkdir -p /home/user/ingest_task/initial_data /home/user/ingest_task/extra_data

# Seed the initial corpus that the executor will use to create the new managed index.
RUN cat > /home/user/ingest_task/initial_data/animals.txt <<'EOF'
Atlantean Wildlife

Cats are domestic feline mammals known for their independent nature.
The Atlantean lynx is the apex predator of the northern forest region.
EOF

RUN cat > /home/user/ingest_task/initial_data/geography.txt <<'EOF'
Atlantean Geography

Mount Pochi is the tallest mountain on the island of Atlantis.
The Crystal River flows from Mount Pochi to the eastern bay.
EOF

# Seed the extra corpus that must be incrementally inserted after the index already exists.
RUN cat > /home/user/ingest_task/extra_data/vehicles.txt <<'EOF'
Atlantean Vehicles

The Atlantis Aurora is a flying car invented in 2031 that uses anti-gravity propulsion.
It can reach speeds of up to 600 kilometers per hour and seats four passengers comfortably.
EOF

RUN cat > /home/user/ingest_task/extra_data/cuisine.txt <<'EOF'
Atlantean Cuisine

The national dish of Atlantis is grilled seaweed wrapped around glowing-blue rice.
Street vendors in Pochi City sell this dish wrapped in palm leaves for easy transport.
EOF

LABEL Author="generate-harbor-tasks"
LABEL Description="LlamaCloud incremental-ingestion Python task: create a managed index from an initial corpus, then insert additional documents and verify they are retrievable."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - LlamaCloud Python SDK: llama-cloud (used by both executor and verifier)
#   - llama-index-core: provides SimpleDirectoryReader and Document for ingestion
#   - llama-index-indices-managed-llama-cloud: provides LlamaCloudIndex managed-index helper (supports incremental insert)
#   - /home/user/ingest_task: project directory for this task
#   - /home/user/ingest_task/initial_data/{animals.txt, geography.txt}: seeded corpus for the initial index creation
#   - /home/user/ingest_task/extra_data/{vehicles.txt, cuisine.txt}: seeded corpus for the incremental insert step
