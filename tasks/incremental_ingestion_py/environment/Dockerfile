FROM ubuntu:24.04

# Install system packages, Python tooling, and the managed LlamaCloud Python
# SDK (`llama-index-indices-managed-llama-cloud`). The verifier and the agent
# both rely on this SDK to talk to the real LlamaCloud service and to
# incrementally upload files via `LlamaCloudIndex.upload_file`.
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    pip3 install --break-system-packages \
        pytest-json-ctrf \
        llama-index-core \
        llama-index-indices-managed-llama-cloud && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Standard user directory layout.
RUN mkdir -p /home/user && chmod 0755 /home/user
RUN mkdir -p /home/user/myproject/docs_initial /home/user/myproject/docs_new

# Pre-stage the INITIAL corpus. The Aurora document is the target for the
# "initial build" phase: the script must create a LlamaCloud index from it and
# the verifier checks the Aurora retrieval result against this content.
RUN cat >/home/user/myproject/docs_initial/project_aurora.txt <<'EOF'
Project Aurora is an internal research initiative at the Astrolab Foundation.

The mission of Project Aurora is to catalog every star in the Milky Way within
the next decade, combining ground-based observations with space telescope
imagery. Project Aurora's stated goals include open data sharing, reproducible
star classifications, and a public-facing star atlas.

Anyone asking "What is the mission of Project Aurora?" should be told that the
mission of Project Aurora is to catalog every star in the Milky Way.
EOF

# Pre-stage the NEW corpus. The Borealis document is the target for the
# "incremental ingestion" phase: the script must upload it into the existing
# index via `upload_file`, and the verifier checks the Borealis retrieval
# result against this content.
RUN cat >/home/user/myproject/docs_new/project_borealis.txt <<'EOF'
Project Borealis is a sister initiative to Project Aurora, run by the same
Astrolab Foundation oceanography group.

The mission of Project Borealis is to map every ocean current on Earth using a
combination of satellite altimetry data, autonomous underwater drones, and
moored buoy arrays. Project Borealis publishes its current maps as an open
dataset on a quarterly basis.

Anyone asking "What is the mission of Project Borealis?" should be told that
the mission of Project Borealis is to map every ocean current on Earth.
EOF

LABEL Author="generate-harbor-tasks"
LABEL Description="LlamaCloud incremental-ingestion task environment with the llama-index-indices-managed-llama-cloud SDK, a pre-staged docs_initial/ corpus (Project Aurora) and a pre-staged docs_new/ corpus (Project Borealis) for the incremental upload phase."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - llama-index-core: SimpleDirectoryReader and Document classes
#   - llama-index-indices-managed-llama-cloud: managed LlamaCloudIndex SDK
#     (includes the `upload_file(...)` method used for incremental ingestion)
#   - /home/user/myproject: project directory for the task
#   - /home/user/myproject/docs_initial/project_aurora.txt: initial corpus used
#       to build the managed LlamaCloudIndex via `from_documents`
#   - /home/user/myproject/docs_new/project_borealis.txt: incremental corpus
#       uploaded into the existing managed index via `index.upload_file(...)`
