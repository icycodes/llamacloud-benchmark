FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages "llama-cloud>=2.1" reportlab

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="LlamaCloud LlamaParse task environment with a sample Quarterly Sales Report PDF pre-generated for parsing."

RUN mkdir -p /home/user/llama_task && \
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
    "/home/user/llama_task/report.pdf",
    pagesize=LETTER,
    title="Quarterly Sales Report",
)

elements = []
elements.append(Paragraph("Quarterly Sales Report", styles["Title"]))
elements.append(Spacer(1, 18))
elements.append(
    Paragraph(
        "This report summarizes the unit sales of our three flagship products for Q3.",
        styles["BodyText"],
    )
)
elements.append(Spacer(1, 18))

data = [
    ["Product", "Units Sold", "Revenue (USD)"],
    ["Widget", "1200", "24000"],
    ["Gadget", "850", "21250"],
    ["Sprocket", "430", "12900"],
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
        "Widget continues to be our top performer, while Sprocket sales remained steady.",
        styles["BodyText"],
    )
)

doc.build(elements)
PYEOF

# Container contents:
#   - Ubuntu 24.04 base with curl, wget, git, python3, pip, pytest, bash
#   - Python packages: llama-cloud (>=2.1) for the LlamaParse SDK; reportlab (build-time, for sample PDF generation)
#   - /home/user/llama_task: project directory for the task
#   - /home/user/llama_task/report.pdf: pre-generated Quarterly Sales Report PDF with a product table (Widget, Gadget, Sprocket)
#   - Expects LLAMA_CLOUD_API_KEY to be supplied at runtime via task.toml

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
