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
RUN mkdir -p /home/user/parse_task

# Generate the deterministic sample.pdf used by this task.
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
    "/home/user/parse_task/sample.pdf",
    pagesize=LETTER,
    title="Quarterly Revenue Report",
)
styles = getSampleStyleSheet()
story = []
story.append(Paragraph("Quarterly Revenue Report", styles["Title"]))
story.append(Spacer(1, 18))
story.append(
    Paragraph(
        "Total revenue for Q3 was $1,234,567 across all business units. "
        "The breakdown by department is shown below.",
        styles["BodyText"],
    )
)
story.append(Spacer(1, 18))

table_data = [
    ["Department", "Revenue (USD)"],
    ["Engineering", "500,000"],
    ["Marketing", "200,000"],
    ["Sales", "400,000"],
    ["Operations", "134,567"],
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
doc.build(story)
PYEOF

LABEL Author="generate-harbor-tasks"
LABEL Description="LlamaCloud LlamaParse Python task: parse a seeded financial PDF to markdown."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - LlamaCloud Python SDK: llama-cloud (>=2.1) for LlamaParse access
#   - reportlab (build-time only) to generate the seeded /home/user/parse_task/sample.pdf
#   - /home/user/parse_task: project directory for this task
#   - /home/user/parse_task/sample.pdf: deterministic test PDF containing the Quarterly Revenue Report fixture
