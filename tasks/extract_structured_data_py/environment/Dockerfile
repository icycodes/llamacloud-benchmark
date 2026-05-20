FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    pip3 install --break-system-packages \
        pytest-json-ctrf \
        "llama-cloud-services" \
        "llama-cloud" \
        "pydantic" && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

RUN mkdir -p /home/user/myproject && \
    cat > /home/user/myproject/sample_resume.txt <<'EOF'
John Smith
Email: john.smith@example.com
Phone: +1-555-0123

Summary:
Senior backend engineer with 8 years of experience building distributed systems.

Skills:
- Python
- Go
- Kubernetes
- PostgreSQL
- AWS

Experience:
- Acme Corp (2019 - Present): Lead engineer on the payments platform.
- WidgetCo (2015 - 2019): Backend developer on the API team.
EOF

LABEL Author="generate-harbor-tasks"
LABEL Description="LlamaCloud LlamaExtract Python task environment with a sample resume seeded under /home/user/myproject."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - LlamaCloud SDKs installed via pip3: llama-cloud-services (LlamaExtract), llama-cloud, pydantic
#   - /home/user/myproject: project directory
#   - /home/user/myproject/sample_resume.txt: pre-seeded sample resume used by the task
