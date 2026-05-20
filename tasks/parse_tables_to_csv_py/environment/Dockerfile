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
RUN mkdir -p /home/user/tables_task

# Generate the deterministic sample.pdf used by this task.
# Page 1: a "Quarterly Department Revenue" table with four data rows.
# Page 2: a "Top Selling Products" table with three data rows.
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
    "/home/user/tables_task/sample.pdf",
    pagesize=LETTER,
    title="Annual Financial Summary",
)
styles = getSampleStyleSheet()
story = []

# Page 1 - Quarterly Department Revenue
story.append(Paragraph("Quarterly Department Revenue", styles["Title"]))
story.append(Spacer(1, 18))
story.append(
    Paragraph(
        "The table below summarizes revenue (in USD) per department for Q1 and Q2.",
        styles["BodyText"],
    )
)
story.append(Spacer(1, 12))

dept_data = [
    ["Department", "Q1 Revenue", "Q2 Revenue"],
    ["Engineering", "100000", "150000"],
    ["Marketing", "50000", "75000"],
    ["Sales", "200000", "250000"],
    ["Operations", "75000", "85000"],
]
dept_table = Table(dept_data, hAlign="LEFT")
dept_table.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ]
    )
)
story.append(dept_table)

# Page 2 - Top Selling Products
story.append(PageBreak())
story.append(Paragraph("Top Selling Products", styles["Title"]))
story.append(Spacer(1, 18))
story.append(
    Paragraph(
        "Unit sales for the flagship product line in the same reporting period.",
        styles["BodyText"],
    )
)
story.append(Spacer(1, 12))

product_data = [
    ["Product", "Units Sold"],
    ["Widget", "1500"],
    ["Gadget", "800"],
    ["Gizmo", "400"],
]
product_table = Table(product_data, hAlign="LEFT")
product_table.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ]
    )
)
story.append(product_table)

doc.build(story)
PYEOF

LABEL Author="generate-harbor-tasks"
LABEL Description="LlamaCloud LlamaParse Python task: extract every table from a seeded two-page PDF into per-table CSV files using expand=['items']."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - LlamaCloud Python SDK: llama-cloud (>=2.1) for LlamaParse access (v2 items tree)
#   - reportlab (build-time only) to generate the seeded /home/user/tables_task/sample.pdf
#   - /home/user/tables_task: project directory for this task
#   - /home/user/tables_task/sample.pdf: deterministic two-page PDF containing two tables (Department Revenue + Top Selling Products)
