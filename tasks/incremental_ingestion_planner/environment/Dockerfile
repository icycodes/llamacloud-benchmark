FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    pip3 install --break-system-packages pytest-json-ctrf "llama-index-indices-managed-llama-cloud>=0.7,<1.0" && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

# Pre-populate the project directory with the fixture input files. We compute the
# baseline SHA-256 for report.md on the fly so previous_state.json always agrees
# with the real on-disk bytes (this is what makes report.md classified as UNCHANGED
# during verification). archive.txt is intentionally absent from the inputs/ folder
# so the planner can correctly emit a DELETE entry for it.
RUN mkdir -p /home/user/sync_planner/inputs && \
    printf '%b' '# Report\nQ3 numbers are strong.' > /home/user/sync_planner/inputs/report.md && \
    printf '%s' 'Internal notes.' > /home/user/sync_planner/inputs/notes.txt && \
    printf '%s' 'fake jpg bytes' > /home/user/sync_planner/inputs/image.jpg && \
    REPORT_SHA="$(sha256sum /home/user/sync_planner/inputs/report.md | awk '{print $1}')" && \
    printf '%s' "{\"index_name\": \"my_index\", \"project_name\": \"Default\", \"files\": [{\"file_name\": \"report.md\", \"sha256\": \"${REPORT_SHA}\"}, {\"file_name\": \"archive.txt\", \"sha256\": \"0000000000000000000000000000000000000000000000000000000000000000\"}]}" > /home/user/sync_planner/previous_state.json

LABEL Author="generate-harbor-tasks"
LABEL Description="LlamaCloud incremental-ingestion-planner task environment with the llama-index managed LlamaCloud SDK preinstalled and a baseline sync state fixture."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - llama-index-indices-managed-llama-cloud (exposes LlamaCloudIndex) for the incremental ingestion task
#   - /home/user/sync_planner: project directory for the task
#   - /home/user/sync_planner/inputs/report.md: fixture markdown file (whose hash is baked into previous_state.json)
#   - /home/user/sync_planner/inputs/notes.txt: new fixture file (no baseline; should be classified as ADD)
#   - /home/user/sync_planner/inputs/image.jpg: unsupported fixture file (must be filtered out)
#   - /home/user/sync_planner/previous_state.json: baseline sync state listing report.md (current hash) and a stale archive.txt entry
