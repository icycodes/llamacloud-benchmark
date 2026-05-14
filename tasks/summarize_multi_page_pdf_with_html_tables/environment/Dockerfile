FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages "llama-cloud>=2.1" reportlab

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="LlamaCloud LlamaParse task environment with a 3-page Operations Report PDF (text intro + two tables on later pages) pre-generated for parsing."

RUN mkdir -p /home/user/ops_report && \
    python3 - <<'PYEOF'
from reportlab.lib.pagesizes import LETTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

styles = getSampleStyleSheet()
doc = SimpleDocTemplate(
    "/home/user/ops_report/operations_report.pdf",
    pagesize=LETTER,
    title="Operations Report Q3",
)

elements = []

# --- Page 1: introduction (no table) ---
elements.append(Paragraph("Operations Report Q3", styles["Title"]))
elements.append(Spacer(1, 18))
elements.append(
    Paragraph(
        "This report summarizes our Q3 operational performance, including product "
        "sales by SKU and a regional breakdown of revenue and headcount. "
        "Each section is presented on its own page so the data tables can be "
        "reviewed independently.",
        styles["BodyText"],
    )
)
elements.append(Spacer(1, 12))
elements.append(
    Paragraph(
        "All figures are preliminary and subject to final audit.",
        styles["BodyText"],
    )
)
elements.append(PageBreak())

# --- Page 2: product sales table ---
elements.append(Paragraph("Product Sales", styles["Heading1"]))
elements.append(Spacer(1, 12))
product_data = [
    ["Product", "Units Sold", "Revenue (USD)"],
    ["Widget", "1200", "24000"],
    ["Gadget", "850", "21250"],
    ["Sprocket", "430", "12900"],
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
elements.append(product_table)
elements.append(PageBreak())

# --- Page 3: regional breakdown table ---
elements.append(Paragraph("Regional Breakdown", styles["Heading1"]))
elements.append(Spacer(1, 12))
region_data = [
    ["Region", "Revenue (USD)", "Headcount"],
    ["NA", "30000", "42"],
    ["EU", "18500", "27"],
    ["APAC", "9650", "14"],
]
region_table = Table(region_data, hAlign="LEFT")
region_table.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ]
    )
)
elements.append(region_table)

doc.build(elements)
PYEOF

# Container contents:
#   - Ubuntu 24.04 base with curl, wget, git, python3, pip, pytest, bash
#   - Python packages: llama-cloud (>=2.1) for the LlamaParse SDK; reportlab (build-time, for sample PDF generation)
#   - /home/user/ops_report: project directory for the task
#   - /home/user/ops_report/operations_report.pdf: pre-generated 3-page Operations Report
#       * Page 1: text-only intro ("Operations Report Q3")
#       * Page 2: "Product Sales" table (Widget / Gadget / Sprocket)
#       * Page 3: "Regional Breakdown" table (NA / EU / APAC)
#   - Expects LLAMA_CLOUD_API_KEY to be supplied at runtime via task.toml

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
