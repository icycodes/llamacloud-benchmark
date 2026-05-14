FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages "llama-cloud>=2.1" "pydantic>=2.5"

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="LlamaCloud LlamaExtract task environment with the llama-cloud SDK and pydantic v2 pre-installed, plus a sample resume.txt to extract."

RUN mkdir -p /home/user/resume_extract && \
    cat >/home/user/resume_extract/resume.txt <<'EOF'
Candidate Name: Jane Doe
Email: jane.doe@example.com
Phone: 555-123-4567

Technical Skills: Python, SQL, AWS, Docker, Kubernetes

Experience:
- Senior Software Engineer at AcmeCorp (2020-Present)
- Software Engineer at Beta Inc (2018-2020)

Education: BS Computer Science, MIT, 2018
EOF

# Container contents:
#   - Ubuntu 24.04 base with curl, wget, git, python3, pip, pytest, bash
#   - Python packages: llama-cloud (>=2.1) for the LlamaCloud SDK, pydantic (>=2.5) for the schema
#   - /home/user/resume_extract/resume.txt: structured plain-text resume to be extracted
#   - Expects LLAMA_CLOUD_API_KEY to be supplied at runtime via task.toml

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
