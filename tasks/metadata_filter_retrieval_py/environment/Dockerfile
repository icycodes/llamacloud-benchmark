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
RUN mkdir -p /home/user/metadata_filter_task/data/finance \
             /home/user/metadata_filter_task/data/sports \
             /home/user/metadata_filter_task/data/geography

# Seed the per-category corpora the executor will ingest into LlamaCloud,
# each with a single distinctive phrase used by the verifier to confirm
# that metadata filtering actually constrains retrieval to the right slice.
RUN cat > /home/user/metadata_filter_task/data/finance/finance.txt <<'EOF'
Finance Brief

Globex Industries reported a Q3 revenue of 6480 dollars in their fiscal report.
The CFO of Globex Industries credited cost discipline and improved logistics for the result.
EOF

RUN cat > /home/user/metadata_filter_task/data/sports/sports.txt <<'EOF'
Sports Brief

Atlas Kim won the 2024 tennis championship in Pochi City.
The crowd cheered Atlas Kim for delivering a record-breaking final-set tiebreak.
EOF

RUN cat > /home/user/metadata_filter_task/data/geography/geography.txt <<'EOF'
Geography Brief

Mount Aurelius is the tallest mountain on the fictional island of Numeria.
Climbers say Mount Aurelius has a permanently snow-capped summit.
EOF

LABEL Author="generate-harbor-tasks"
LABEL Description="LlamaCloud managed-index task: ingest documents with explicit category metadata and retrieve from the index using LlamaIndex MetadataFilters."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - LlamaCloud Python SDK: llama-cloud (used by both executor and verifier)
#   - llama-index-core: provides Document, SimpleDirectoryReader, and MetadataFilters
#   - llama-index-indices-managed-llama-cloud: provides LlamaCloudIndex managed-index helper
#   - /home/user/metadata_filter_task: project directory for this task
#   - /home/user/metadata_filter_task/data/{finance,sports,geography}/*.txt: per-category seed corpora
