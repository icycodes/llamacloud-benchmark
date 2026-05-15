FROM ubuntu:24.04

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

RUN mkdir -p /home/user && chmod 0755 /home/user
RUN mkdir -p /home/user/extract_task

# Generate the deterministic sample.pdf used by this task. The PDF is a
# fictional ACME Corporation invoice for "Globex Industries" with a
# four-row line-item table on page 2 and a grand total of 425.00.
RUN python3 - <<'PYEOF'
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)

doc = SimpleDocTemplate(
    "/home/user/extract_task/sample.pdf",
    pagesize=LETTER,
    title="ACME Corp Invoice INV-2024-7788",
)
styles = getSampleStyleSheet()
story = []

# Page 1 - header
story.append(Paragraph("ACME Corporation - Invoice", styles["Title"]))
story.append(Spacer(1, 18))
story.append(Paragraph("Invoice number: INV-2024-7788", styles["BodyText"]))
story.append(Paragraph("Bill to customer: Globex Industries", styles["BodyText"]))
story.append(Paragraph("Customer email: billing@globex.example", styles["BodyText"]))
story.append(Spacer(1, 18))
story.append(
    Paragraph(
        "Thank you for your business. The detailed line items for this invoice "
        "are listed on the following page.",
        styles["BodyText"],
    )
)
story.append(PageBreak())

# Page 2 - line items table
story.append(Paragraph("Line Items", styles["Heading1"]))
story.append(Spacer(1, 12))
table_data = [
    ["Item", "Quantity", "Unit Price (USD)", "Line Total (USD)"],
    ["Widget A", "3", "25.00", "75.00"],
    ["Gadget B", "2", "50.00", "100.00"],
    ["Service C", "1", "200.00", "200.00"],
    ["License D", "4", "12.50", "50.00"],
    ["Grand Total", "", "", "425.00"],
]
table = Table(table_data, hAlign="LEFT")
table.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ]
    )
)
story.append(table)

doc.build(story)
PYEOF

LABEL Author="generate-harbor-tasks"
LABEL Description="LlamaCloud LlamaExtract Python task: extract a structured invoice from a seeded multi-page PDF using a Pydantic schema."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - LlamaCloud Python SDK: llama-cloud (>=2.1) for LlamaExtract access
#   - pydantic (>=2) for defining the extraction data schema
#   - reportlab (build-time only) to generate the seeded /home/user/extract_task/sample.pdf
#   - /home/user/extract_task: project directory for this task
#   - /home/user/extract_task/sample.pdf: deterministic test invoice PDF (Globex Industries, INV-2024-7788, total 425.00)
