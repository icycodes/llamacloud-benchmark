FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    pip3 install --break-system-packages \
        pytest-json-ctrf \
        requests \
        reportlab \
        "llama-cloud>=2.1" && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

# Seed the project directory and synthesize the input PDF the task will parse.
# We embed the PDF generator as a one-shot heredoc; reportlab produces a real PDF
# whose textual content (title + revenue line + outlook paragraph) is what the
# task verifier checks for in the parsed markdown.
RUN mkdir -p /home/user/myproject && \
    python3 - <<'PYEOF'
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas

PDF_PATH = "/home/user/myproject/quarterly_report.pdf"

c = canvas.Canvas(PDF_PATH, pagesize=LETTER)
width, height = LETTER

# Title
c.setFont("Helvetica-Bold", 20)
c.drawString(72, height - 96, "ACME CORP QUARTERLY REPORT")

# Body content
c.setFont("Helvetica", 12)
c.drawString(72, height - 144, "Total revenue for Q3 was 12345 USD.")
c.drawString(72, height - 168, "Operating expenses remained flat compared to Q2.")
c.drawString(72, height - 192, "Outlook: ACME Corp expects steady growth into Q4 of fiscal year 2026.")
c.drawString(72, height - 216, "Prepared by the ACME Finance Team.")

c.showPage()
c.save()
PYEOF

LABEL Author="generate-harbor-tasks"
LABEL Description="LlamaCloud (LlamaParse) Python task environment with a seeded synthetic PDF in /home/user/myproject."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - llama-cloud (>=2.1) installed via pip3 for the LlamaParse Python SDK
#   - requests installed via pip3 for verifier REST API calls
#   - reportlab installed via pip3 to synthesize the seeded /home/user/myproject/quarterly_report.pdf at build time
#   - /home/user/myproject: project directory expected by the task
#   - /home/user/myproject/quarterly_report.pdf: synthetic one-page PDF with deterministic content used by both task and verifier
