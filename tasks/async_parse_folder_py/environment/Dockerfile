FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    pip3 install --break-system-packages \
        pytest-json-ctrf \
        llama-parse==0.5.20 \
        llama-index-core \
        reportlab && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

# Create the project layout and three sample PDFs the executor must parse.
RUN mkdir -p /home/user/myproject/input_pdfs && \
    python3 - <<'PYEOF'
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

documents = {
    "/home/user/myproject/input_pdfs/doc_alpha.pdf": [
        "Alpha Quarterly Report",
        "This is the alpha quarterly report.",
        "Alpha report sentinel ABC-123",
        "Confidential - internal use only.",
    ],
    "/home/user/myproject/input_pdfs/doc_beta.pdf": [
        "Beta Project Summary",
        "Summary of beta project deliverables.",
        "Beta report sentinel BETA-456",
        "Reviewed by the product team.",
    ],
    "/home/user/myproject/input_pdfs/doc_gamma.pdf": [
        "Gamma Research Notes",
        "Notes on gamma experimental results.",
        "Gamma report sentinel GAMMA-789",
        "Findings should be reproduced before publication.",
    ],
}

for path, lines in documents.items():
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter
    text = c.beginText(72, height - 96)
    text.setFont("Helvetica", 14)
    for line in lines:
        text.textLine(line)
    c.drawText(text)
    c.showPage()
    c.save()
PYEOF

LABEL Author="generate-harbor-tasks"
LABEL Description="LlamaCloud LlamaParse async folder parsing task environment with three pre-built sample PDFs."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - llama-parse (LlamaCloud LlamaParse SDK) and llama-index-core installed via pip3
#   - reportlab installed only to seed deterministic sample PDFs at build time
#   - /home/user/myproject: project directory the executor will work in
#   - /home/user/myproject/input_pdfs/{doc_alpha,doc_beta,doc_gamma}.pdf: sample PDFs with sentinel strings
