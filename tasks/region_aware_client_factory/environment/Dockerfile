FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages "llama-cloud>=2.1"

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="LlamaCloud region-aware client factory task environment with the llama-cloud SDK pre-installed."

RUN mkdir -p /home/user/region_setup

# Container contents:
#   - Ubuntu 24.04 base with curl, wget, git, python3, pip, pytest, bash
#   - Python packages: llama-cloud (>=2.1) for the LlamaCloud SDK (provides the LlamaCloud client class)
#   - /home/user/region_setup: empty project directory the agent must populate with client_factory.py and run.py
#   - Expects LLAMA_CLOUD_API_KEY to be supplied at runtime via task.toml

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
