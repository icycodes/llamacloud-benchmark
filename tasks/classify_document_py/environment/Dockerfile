FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    pip3 install --break-system-packages \
        pytest-json-ctrf \
        "llama-cloud>=1.6" && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

# Create the project directory and pre-populate document.txt used by the task and verifier.
RUN mkdir -p /home/user/myproject && \
    printf '%s\n' \
        'INVOICE #INV-2024-001' \
        'Invoice Date: 2024-03-15' \
        'Bill To: Acme Corp.' \
        '' \
        'Line Items:' \
        '- Consulting Services (10 hours) ... $1,500.00' \
        '- Software License (Annual) ........ $1,200.00' \
        '' \
        'Subtotal: $2,700.00' \
        'Tax (10%): $270.00' \
        'Total: $2,970.00' \
        > /home/user/myproject/document.txt

LABEL Author="generate-harbor-tasks"
LABEL Description="LlamaCloud (LlamaClassify) Python SDK task environment with a pre-populated invoice document at /home/user/myproject/document.txt."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - llama-cloud (>=1.6): the LlamaCloud Python SDK that provides the LlamaClassify client
#   - /home/user/myproject: project working directory for the task
#   - /home/user/myproject/document.txt: pre-populated invoice text file used by both
#       the task executor and the verifier
