FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    pip3 install --break-system-packages \
        pytest-json-ctrf \
        "llama-cloud>=2.1" \
        "reportlab>=4.0" && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user
RUN mkdir -p /home/user/screenshot_task

# Seed a deterministic 3-page PDF used as the parse input.
# Each page contains a distinct marker phrase so the verifier can confirm
# the right document was parsed. Generated at image build time so it is
# byte-identical across runs.
RUN python3 - <<'PYEOF'
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

PATH = "/home/user/screenshot_task/sample.pdf"
PAGE_TEXTS = [
    "Screenshot-Mode-Page-One",
    "Screenshot-Mode-Page-Two",
    "Screenshot-Mode-Page-Three",
]

c = canvas.Canvas(PATH, pagesize=letter)
width, height = letter
for idx, marker in enumerate(PAGE_TEXTS, start=1):
    c.setFont("Helvetica-Bold", 28)
    c.drawString(72, height - 100, f"Atlantis Quarterly Report - Page {idx}")
    c.setFont("Helvetica", 18)
    c.drawString(72, height - 160, marker)
    c.setFont("Helvetica", 14)
    c.drawString(
        72,
        height - 220,
        "This page is included in a multi-page PDF used to verify the LlamaParse",
    )
    c.drawString(
        72,
        height - 240,
        "screenshot output option (output_options.images_to_save).",
    )
    c.setFont("Helvetica-Oblique", 12)
    c.drawString(
        72,
        height - 300,
        f"Page {idx} of {len(PAGE_TEXTS)} - marker: {marker}",
    )
    c.showPage()
c.save()
PYEOF

LABEL Author="generate-harbor-tasks"
LABEL Description="LlamaCloud LlamaParse Python task: parse a 3-page PDF with screenshots enabled and save every per-page PNG to disk."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - LlamaCloud Python SDK: llama-cloud (used by both executor and verifier)
#   - reportlab: used only at image build time to generate the deterministic 3-page sample PDF
#   - /home/user/screenshot_task: project directory for this task
#   - /home/user/screenshot_task/sample.pdf: 3-page PDF with distinct marker phrases on each page
