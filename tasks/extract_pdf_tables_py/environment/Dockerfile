FROM ubuntu:24.04

# Install system packages, Python tooling, the official LlamaCloud Python SDK
# (`llama-cloud`, exposing the synchronous `LlamaCloud()` client used by the
# task), and `reportlab` which we use during image build to fabricate the
# multi-page financial report PDF fixture.
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    pip3 install --break-system-packages \
        pytest-json-ctrf \
        "llama-cloud>=2.1" \
        reportlab && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Standard user directory layout.
RUN mkdir -p /home/user && chmod 0755 /home/user
RUN mkdir -p /home/user/myproject

# Pre-stage a deterministic multi-page report PDF that contains two tables.
# Page 1 -> "Revenue by Product" with rows including Widget A, Widget B, Service Plan.
# Page 2 -> "Regional Sales" with rows including North America, Europe, Asia Pacific.
RUN python3 - <<'PY'
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
)
from reportlab.lib import colors

styles = getSampleStyleSheet()
doc = SimpleDocTemplate("/home/user/myproject/report.pdf", pagesize=LETTER)

story = []

# --- Page 1: Revenue by Product ---
story.append(Paragraph("FY2024 Quarterly Performance Report", styles["Title"]))
story.append(Spacer(1, 18))
story.append(Paragraph("Revenue by Product", styles["Heading2"]))
story.append(Spacer(1, 12))
story.append(Paragraph(
    "The following table summarizes the quarterly revenue (in US dollars) "
    "for each product line during the first half of fiscal year 2024.",
    styles["BodyText"],
))
story.append(Spacer(1, 12))

revenue_data = [
    ["Product", "Q1 Revenue (USD)", "Q2 Revenue (USD)"],
    ["Widget A", "120,000", "135,500"],
    ["Widget B", "98,750", "104,300"],
    ["Service Plan", "210,000", "225,000"],
]
revenue_table = Table(revenue_data, hAlign="LEFT")
revenue_table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
]))
story.append(revenue_table)

story.append(PageBreak())

# --- Page 2: Regional Sales ---
story.append(Paragraph("Regional Sales", styles["Heading2"]))
story.append(Spacer(1, 12))
story.append(Paragraph(
    "The following table summarizes unit sales by geographic region for "
    "Q1 and Q2 of fiscal year 2024.",
    styles["BodyText"],
))
story.append(Spacer(1, 12))

region_data = [
    ["Region", "Q1 Units", "Q2 Units"],
    ["North America", "8,400", "9,250"],
    ["Europe", "5,100", "5,650"],
    ["Asia Pacific", "6,800", "7,400"],
]
region_table = Table(region_data, hAlign="LEFT")
region_table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
]))
story.append(region_table)

doc.build(story)
PY

LABEL Author="generate-harbor-tasks"
LABEL Description="LlamaCloud LlamaParse table-extraction task environment with the llama-cloud Python SDK and a pre-staged two-page report.pdf in /home/user/myproject."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - llama-cloud: official LlamaCloud Python SDK used by the task
#   - reportlab: only used at build time to generate the report.pdf fixture
#   - /home/user/myproject: project directory for the task
#   - /home/user/myproject/report.pdf: pre-staged two-page PDF containing
#       the title `FY2024 Quarterly Performance Report`, a `Revenue by Product`
#       table on page 1, and a `Regional Sales` table on page 2
