FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    pip3 install --break-system-packages \
        pytest-json-ctrf \
        "llama-cloud>=2.1" \
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
c.drawString(72, 690, "This single-page PDF is used to verify an asynchronous LlamaParse pipeline.")
c.drawString(72, 670, "It contains the phrase 'Hello LlamaParse' for verification.")
c.showPage()
c.save()
PY

LABEL Author="generate-harbor-tasks"
LABEL Description="LlamaCloud (LlamaParse) Python async-SDK task environment with a pre-generated sample.pdf at /home/user/myproject/sample.pdf."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - llama-cloud (>=2.1): the LlamaCloud Python SDK that provides both LlamaCloud and AsyncLlamaCloud clients
#   - reportlab: used at build time to generate the sample PDF
#   - /home/user/myproject: project working directory for the task
#   - /home/user/myproject/sample.pdf: pre-generated one-page PDF containing
#       'Hello LlamaParse - Harbor Test Document' used by both the task executor and the verifier
