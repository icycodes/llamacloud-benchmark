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
RUN mkdir -p /home/user/prompted_parse_task

# Generate the deterministic receipt PDF used by this task. The receipt contains
# (1) a merchant header block, (2) a noisy promotional / survey-code block that
# the executor must instruct LlamaParse to drop, (3) a line-item table with three
# items, and (4) a totals block with the final Total of $17.36.
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
    "/home/user/prompted_parse_task/sample.pdf",
    pagesize=LETTER,
    title="McDonald's Restaurant Receipt",
)
styles = getSampleStyleSheet()
story = []

# 1. Merchant header (noise we want filtered out).
story.append(Paragraph("McDonald's Restaurant #312782", styles["Title"]))
story.append(Spacer(1, 6))
story.append(Paragraph("378 PINE RD NW, RICE, MN 56367-9740", styles["Normal"]))
story.append(Paragraph("TEL# 320 393 4600", styles["Normal"]))
story.append(Spacer(1, 18))

# 2. Promotional / survey block (noise that the custom_prompt must drop).
story.append(
    Paragraph(
        "Rate us HIGHLY SATISFIED and receive ONE FREE ITEM. "
        "Purchase any sandwich and receive an item of equal or lesser value. "
        "Go to www.mcdvoice.com within 7 days and tell us about your visit. "
        "Survey Code: 31278-01121-21018-20481-00081-0.",
        styles["BodyText"],
    )
)
story.append(Spacer(1, 18))

# 3. Line-item table.
table_data = [
    ["Item", "Price"],
    ["Big Mac Meal", "$8.99"],
    ["Snack Oreo McFlurry", "$2.69"],
    ["Happy Meal 6 Pc", "$4.89"],
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

# 4. Totals block. Subtotal + Tax = Total ($17.36).
totals_data = [
    ["Subtotal", "$16.57"],
    ["Tax", "$0.79"],
    ["Total", "$17.36"],
]
totals = Table(totals_data, hAlign="LEFT")
totals.setStyle(
    TableStyle(
        [
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
            ("FONTNAME", (0, 2), (-1, 2), "Helvetica-Bold"),
        ]
    )
)
story.append(totals)
story.append(Spacer(1, 18))

# Footer noise.
story.append(
    Paragraph(
        "***NOW ACCEPTING APPLICATIONS*** text to #36453, apply31278.",
        styles["BodyText"],
    )
)

doc.build(story)
PYEOF

LABEL Author="generate-harbor-tasks"
LABEL Description="LlamaCloud LlamaParse custom_prompt Python task: parse a seeded receipt PDF using a natural-language custom_prompt to extract only the line items and final total."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - LlamaCloud Python SDK: llama-cloud (>=2.1) for LlamaParse access (used by both executor and verifier)
#   - reportlab (build-time only) to generate the seeded /home/user/prompted_parse_task/sample.pdf
#   - /home/user/prompted_parse_task: project directory for this task
#   - /home/user/prompted_parse_task/sample.pdf: deterministic receipt PDF fixture with three line items and a $17.36 total
