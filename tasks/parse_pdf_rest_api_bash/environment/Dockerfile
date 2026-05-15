FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep jq && \
    pip3 install --break-system-packages \
        pytest-json-ctrf \
        requests \
        reportlab && \
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
c.drawString(72, 690, "This single-page PDF is used to verify a LlamaParse REST API pipeline.")
c.drawString(72, 670, "It contains the phrase 'Hello LlamaParse' for verification.")
c.showPage()
c.save()
PY

LABEL Author="generate-harbor-tasks"
LABEL Description="LlamaCloud REST API task environment with curl, jq, and a pre-generated sample.pdf in /home/user/myproject."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - jq: used by the task's bash script to parse JSON responses from the LlamaCloud REST API
#   - requests (pip3): used by the final-state pytest tests to call the LlamaCloud REST API directly
#   - reportlab (pip3): used at build time to generate the sample PDF
#   - /home/user/myproject: project working directory for the task
#   - /home/user/myproject/sample.pdf: pre-generated one-page PDF containing
#       'Hello LlamaParse - Harbor Test Document' used by both the task executor and the verifier
