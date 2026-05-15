FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    pip3 install --break-system-packages \
        pytest-json-ctrf \
        reportlab && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

# Create the project directory and pre-generate the sample PDF used by the task and verifier.
RUN mkdir -p /home/user/myproject && \
    python3 - <<'PY'
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

path = "/home/user/myproject/sample.pdf"
c = canvas.Canvas(path, pagesize=letter)
c.setFont("Helvetica-Bold", 18)
c.drawString(72, 720, "Hello LlamaParse - Harbor Test Document")
c.setFont("Helvetica", 12)
c.drawString(72, 690, "This single-page PDF is used to verify a LlamaParse parsing pipeline.")
c.drawString(72, 670, "It contains the phrase 'Hello LlamaParse' for verification.")
c.showPage()
c.save()
PY

# Initialize the Node.js TypeScript project with @llamaindex/llama-cloud and tsx pre-installed.
# This avoids requiring the task executor to run `npm install` at task time.
RUN cd /home/user/myproject && \
    cat >package.json <<'EOF'
{
  "name": "myproject",
  "version": "1.0.0",
  "type": "module",
  "private": true,
  "dependencies": {
    "@llamaindex/llama-cloud": "^0.4.0"
  },
  "devDependencies": {
    "tsx": "^4.19.0",
    "typescript": "^5.5.0",
    "@types/node": "^20.0.0"
  }
}
EOF

RUN cd /home/user/myproject && npm install --no-audit --no-fund --loglevel=error

LABEL Author="generate-harbor-tasks"
LABEL Description="LlamaCloud (LlamaParse) TypeScript SDK task environment with a pre-generated sample.pdf, Node.js v24, and @llamaindex/llama-cloud + tsx pre-installed in /home/user/myproject."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - reportlab: used at build time to generate the sample PDF
#   - Node.js v24 for running the @llamaindex/llama-cloud TypeScript SDK
#   - /home/user/myproject: project working directory with package.json ("type": "module") and node_modules
#   - /home/user/myproject/sample.pdf: pre-generated one-page PDF containing
#       'Hello LlamaParse - Harbor Test Document' used by both the task executor and the verifier
#   - /home/user/myproject/node_modules/@llamaindex/llama-cloud: pre-installed TypeScript SDK
#   - /home/user/myproject/node_modules/.bin/tsx: pre-installed TypeScript runner used via `npx tsx`
