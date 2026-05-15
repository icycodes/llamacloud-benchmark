FROM ubuntu:24.04

# Install system packages, Python tooling, the official LlamaCloud Python SDK
# (`llama-cloud`, exposing the `LlamaCloud()` client with the `client.extract`
# and `client.files` namespaces used by the task), `pydantic` for schema
# definition, and `reportlab` which we use during image build to fabricate
# the one-page invoice PDF fixture deterministically.
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    pip3 install --break-system-packages \
        pytest-json-ctrf \
        "llama-cloud>=2.1" \
        "pydantic>=2" \
        reportlab && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Standard user directory layout.
RUN mkdir -p /home/user && chmod 0755 /home/user
RUN mkdir -p /home/user/myproject

# Pre-stage a deterministic one-page invoice PDF used as the LlamaExtract input.
# Fields are intentionally chosen so the extraction can be validated deterministically:
#   - Invoice Number: INV-2024-0042
#   - Invoice Date:   2024-03-15
#   - Vendor:         Acme Corporation
#   - Bill To:        Globex Industries
#   - Line items:
#       Widget Type A                      10  25.00     250.00
#       Service Hours - Onsite Support      8  120.00    960.00
#       Annual Maintenance Plan             1  500.00    500.00
#   - Subtotal: 1710.00 | Tax (8%): 136.80 | Total: 1846.80
RUN python3 - <<'PY'
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
)
from reportlab.lib import colors

styles = getSampleStyleSheet()
doc = SimpleDocTemplate("/home/user/myproject/invoice.pdf", pagesize=LETTER)

story = []

# --- Header ---
story.append(Paragraph("INVOICE", styles["Title"]))
story.append(Spacer(1, 18))

# --- Metadata block ---
meta_lines = [
    "Invoice Number: INV-2024-0042",
    "Invoice Date: 2024-03-15",
    "",
    "Vendor: Acme Corporation",
    "123 Industrial Way, Springfield, IL 62701",
    "",
    "Bill To: Globex Industries",
    "500 Corporate Plaza, Metropolis, NY 10001",
]
for line in meta_lines:
    story.append(Paragraph(line if line else "&nbsp;", styles["BodyText"]))

story.append(Spacer(1, 18))
story.append(Paragraph("Line Items", styles["Heading2"]))
story.append(Spacer(1, 8))

line_item_data = [
    ["Description", "Quantity", "Unit Price (USD)", "Amount (USD)"],
    ["Widget Type A", "10", "25.00", "250.00"],
    ["Service Hours - Onsite Support", "8", "120.00", "960.00"],
    ["Annual Maintenance Plan", "1", "500.00", "500.00"],
]
line_item_table = Table(line_item_data, hAlign="LEFT")
line_item_table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
]))
story.append(line_item_table)

story.append(Spacer(1, 18))

# --- Totals block ---
totals_lines = [
    "Subtotal: 1710.00",
    "Tax (8%): 136.80",
    "Total: 1846.80",
]
for line in totals_lines:
    story.append(Paragraph(line, styles["BodyText"]))

doc.build(story)
PY

LABEL Author="generate-harbor-tasks"
LABEL Description="LlamaCloud LlamaExtract structured-extraction task environment with the llama-cloud Python SDK, pydantic, and a pre-staged invoice.pdf in /home/user/myproject."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - llama-cloud: official LlamaCloud Python SDK used by the task (LlamaExtract via client.extract)
#   - pydantic: used by the agent to define the extraction schema
#   - reportlab: only used at build time to generate the invoice.pdf fixture
#   - /home/user/myproject: project directory for the task
#   - /home/user/myproject/invoice.pdf: pre-staged one-page invoice PDF with
#       Invoice Number INV-2024-0042, Vendor Acme Corporation, Bill To Globex
#       Industries, three line items, and a Total of 1846.80
