FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages "llama-cloud>=2.1" reportlab

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="LlamaCloud LlamaParse task environment with a pre-generated 4-page product catalog PDF for partial-page parsing (target_pages)."

RUN mkdir -p /home/user/catalog_task && \
    python3 - <<'PYEOF'
from reportlab.lib.pagesizes import LETTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    Table,
    TableStyle,
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

styles = getSampleStyleSheet()
doc = SimpleDocTemplate(
    "/home/user/catalog_task/catalog.pdf",
    pagesize=LETTER,
    title="Product Catalog",
)

pages = [
    ("Catalog Page 1", "Widget",   "$10"),
    ("Catalog Page 2", "Bracket",  "$15"),
    ("Catalog Page 3", "Sprocket", "$20"),
    ("Catalog Page 4", "Dynamo",   "$25"),
]

elements = []
for i, (heading, product, price) in enumerate(pages):
    elements.append(Paragraph(heading, styles["Title"]))
    elements.append(Spacer(1, 18))
    elements.append(
        Paragraph(
            f"This page describes our flagship product: {product}.",
            styles["BodyText"],
        )
    )
    elements.append(Spacer(1, 12))
    table = Table(
        [["Product", "Price"], [product, price]],
        hAlign="LEFT",
    )
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
    elements.append(table)
    if i != len(pages) - 1:
        elements.append(PageBreak())

doc.build(elements)
PYEOF

# Container contents:
#   - Ubuntu 24.04 base with curl, wget, git, python3, pip, pytest, bash
#   - Python packages: llama-cloud (>=2.1) for the LlamaParse SDK; reportlab (build-time, for sample PDF generation)
#   - /home/user/catalog_task: project directory for the task
#   - /home/user/catalog_task/catalog.pdf: 4-page product catalog PDF
#       Page 1 -> Widget   ($10)
#       Page 2 -> Bracket  ($15)
#       Page 3 -> Sprocket ($20)
#       Page 4 -> Dynamo   ($25)
#   - Expects LLAMA_CLOUD_API_KEY to be supplied at runtime via task.toml

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
