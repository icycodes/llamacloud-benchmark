FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    pip3 install --break-system-packages \
        pytest-json-ctrf \
        "llama-cloud>=2.1" \
        "pydantic>=2.0" \
        reportlab && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user
RUN mkdir -p /home/user/extract_task

# Generate the deterministic invoice.pdf used by this task.
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
)

doc = SimpleDocTemplate(
    "/home/user/extract_task/invoice.pdf",
    pagesize=LETTER,
    title="Invoice INV-2024-7842",
)
styles = getSampleStyleSheet()
story = []
story.append(Paragraph("Invoice #INV-2024-7842", styles["Title"]))
story.append(Spacer(1, 12))
story.append(Paragraph("Date: 2024-07-15", styles["BodyText"]))
story.append(Spacer(1, 12))
story.append(Paragraph("From: Pochi Industries Ltd.", styles["BodyText"]))
story.append(Paragraph("Bill To: Atlantis Trading Co.", styles["BodyText"]))
story.append(Spacer(1, 18))

table_data = [
    ["Description", "Amount (USD)"],
    ["Consulting services", "4,200.00"],
    ["Implementation fee", "1,800.00"],
]
table = Table(table_data, hAlign="LEFT")
table.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ]
    )
)
story.append(table)
story.append(Spacer(1, 18))
story.append(Paragraph("Subtotal: $6,000.00", styles["BodyText"]))
story.append(Paragraph("Tax: $480.00", styles["BodyText"]))
story.append(Paragraph("Total Due: $6,480.00 USD", styles["Heading3"]))
doc.build(story)
PYEOF

LABEL Author="generate-harbor-tasks"
LABEL Description="LlamaCloud LlamaExtract Python task: extract structured invoice data from a seeded PDF into a Pydantic-schemas JSON file."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - LlamaCloud Python SDK: llama-cloud (provides client.files, client.extract used by the task and verifier)
#   - pydantic v2: required by the executor to define the Invoice schema
#   - reportlab (build-time use) to generate the seeded /home/user/extract_task/invoice.pdf
#   - /home/user/extract_task: project directory for this task
#   - /home/user/extract_task/invoice.pdf: deterministic invoice fixture containing Pochi Industries / Atlantis Trading / INV-2024-7842 / Total $6,480.00 USD
