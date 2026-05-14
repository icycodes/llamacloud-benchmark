FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages "llama-cloud>=2.1" reportlab

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="LlamaCloud LlamaParse task environment with a sample Q3 Product Sales PDF pre-generated for structured table extraction."

RUN mkdir -p /home/user/sales_extraction && \
    python3 - <<'PYEOF'
from reportlab.lib.pagesizes import LETTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

styles = getSampleStyleSheet()
doc = SimpleDocTemplate(
    "/home/user/sales_extraction/quarterly_sales.pdf",
    pagesize=LETTER,
    title="Q3 Product Sales",
)

elements = []
elements.append(Paragraph("Q3 Product Sales", styles["Title"]))
elements.append(Spacer(1, 18))
elements.append(
    Paragraph(
        "The table below reports unit sales and revenue for our four flagship products in Q3.",
        styles["BodyText"],
    )
)
elements.append(Spacer(1, 18))

data = [
    ["Product", "Units Sold", "Revenue (USD)"],
    ["Widget", "1200", "24000"],
    ["Gadget", "850", "21250"],
    ["Sprocket", "430", "12900"],
    ["Cog", "670", "18760"],
]
table = Table(data, hAlign="LEFT")
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
elements.append(Spacer(1, 18))
elements.append(
    Paragraph(
        "Widget remained the top performer this quarter while Cog showed strong improvement.",
        styles["BodyText"],
    )
)

doc.build(elements)
PYEOF

# Container contents:
#   - Ubuntu 24.04 base with curl, wget, git, python3, pip, pytest, bash
#   - Python packages: llama-cloud (>=2.1) for the LlamaParse SDK; reportlab (build-time, for sample PDF generation)
#   - /home/user/sales_extraction: project directory for the task
#   - /home/user/sales_extraction/quarterly_sales.pdf: pre-generated Q3 Product Sales PDF with a 4-row product table
#     (Widget, Gadget, Sprocket, Cog) including Units Sold and Revenue (USD)
#   - Expects LLAMA_CLOUD_API_KEY to be supplied at runtime via task.toml

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
