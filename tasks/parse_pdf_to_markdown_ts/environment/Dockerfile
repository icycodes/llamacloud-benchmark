FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    npm install -g tsx typescript && \
    pip3 install --break-system-packages pytest-json-ctrf reportlab && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

RUN mkdir -p /home/user/myproject/fixtures && \
    python3 -c "from reportlab.pdfgen import canvas; \
c = canvas.Canvas('/home/user/myproject/fixtures/sample.pdf'); \
c.drawString(100, 750, 'Hello LlamaCloud'); \
c.drawString(100, 720, 'This is a sample PDF used to verify the LlamaCloud Parse TypeScript task.'); \
c.showPage(); \
c.save()"

LABEL Author="generate-harbor-tasks"
LABEL Description="Node.js v24 environment for the LlamaCloud Parse TypeScript task, with a fixture PDF prepared under /home/user/myproject/fixtures."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - Node.js v24 (provides node, npm, npx) for the TypeScript task environment
#   - global npm packages: tsx, typescript (so `npx tsx` runs offline)
#   - python helper: reportlab (only used at build time to generate the fixture PDF)
#   - /home/user/myproject: working directory for the task
#   - /home/user/myproject/fixtures/sample.pdf: small PDF containing the literal text "Hello LlamaCloud"
