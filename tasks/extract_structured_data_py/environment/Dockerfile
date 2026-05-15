FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    pip3 install --break-system-packages \
        pytest-json-ctrf \
        "llama-cloud>=2.1" \
        "pydantic>=2" && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

# Create the project directory and pre-populate candidate.txt used by the task and verifier.
RUN mkdir -p /home/user/myproject && \
    printf '%s\n' \
        'Candidate Name: Alice Johnson' \
        'Email: alice.johnson@example.com' \
        'Skills: Python, Machine Learning, Docker, Kubernetes' \
        > /home/user/myproject/candidate.txt

LABEL Author="generate-harbor-tasks"
LABEL Description="LlamaCloud (LlamaExtract) Python SDK task environment with a pre-populated candidate.txt at /home/user/myproject/candidate.txt."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - llama-cloud (>=2.1): the LlamaCloud Python SDK that provides the LlamaExtract client
#   - pydantic (>=2): used by the task script to define the extraction schema
#   - /home/user/myproject: project working directory for the task
#   - /home/user/myproject/candidate.txt: pre-populated candidate text file with known fields
#       (name, email, skills) used by both the task executor and the verifier
