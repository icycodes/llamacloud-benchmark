FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    pip3 install --break-system-packages pytest-json-ctrf "llama-cloud-services>=0.6,<1.0" && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

# Pre-populate the project directory with the fixture input files.
RUN mkdir -p /home/user/parse_planner/inputs && \
    printf '%s' 'Sample data for parsing.' > /home/user/parse_planner/inputs/data.txt && \
    printf '%b' '# Notes\nHello world' > /home/user/parse_planner/inputs/notes.md && \
    printf '%s' 'fake image bytes' > /home/user/parse_planner/inputs/image.jpg

LABEL Author="generate-harbor-tasks"
LABEL Description="LlamaCloud parse-plan-builder task environment with llama-cloud-services SDK preinstalled and fixture input documents."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - llama-cloud-services Python SDK (which exposes LlamaParse) for the parse plan task
#   - /home/user/parse_planner: project directory for the task
#   - /home/user/parse_planner/inputs/data.txt: fixture text file (24 bytes, no trailing newline)
#   - /home/user/parse_planner/inputs/notes.md: fixture markdown file (19 bytes, no trailing newline)
#   - /home/user/parse_planner/inputs/image.jpg: unsupported fixture file (16 bytes, used to verify filtering)
