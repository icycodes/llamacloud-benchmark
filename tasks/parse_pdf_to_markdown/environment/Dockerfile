FROM ubuntu:24.04

# Install system packages, Python, and required Python libraries (including the
# LlamaParse SDK `llama-cloud-services`, plus `reportlab` which we use during
# image build to fabricate the sample.pdf fixture).
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    pip3 install --break-system-packages \
        pytest-json-ctrf \
        llama-cloud-services \
        reportlab && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Standard user directory layout.
RUN mkdir -p /home/user && chmod 0755 /home/user
RUN mkdir -p /home/user/myproject

# Pre-stage the sample PDF that the agent's script must parse. The PDF has a
# top-level title `Quarterly Sales Report` and a small revenue table so that the
# parsed markdown is deterministic and easy to verify.
RUN python3 - <<'PY'
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

styles = getSampleStyleSheet()
doc = SimpleDocTemplate("/home/user/myproject/sample.pdf", pagesize=LETTER)

story = []
story.append(Paragraph("Quarterly Sales Report", styles["Title"]))
story.append(Spacer(1, 18))
story.append(Paragraph(
    "This short report summarizes quarterly revenue across product lines. "
    "It is used as a test fixture for document parsing pipelines.",
    styles["BodyText"],
))
story.append(Spacer(1, 18))

data = [
    ["Product", "Q1 Revenue (USD)", "Q2 Revenue (USD)"],
    ["Widget A", "120,000", "135,500"],
    ["Widget B", "98,750", "104,300"],
    ["Service Plan", "210,000", "225,000"],
]
table = Table(data, hAlign="LEFT")
table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
]))
story.append(table)

doc.build(story)
PY

LABEL Author="generate-harbor-tasks"
LABEL Description="LlamaParse PDF-to-Markdown task environment with the llama-cloud-services SDK and a pre-staged sample.pdf in /home/user/myproject."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - llama-cloud-services: LlamaParse Python SDK used by the task
#   - reportlab: only used at build time to generate the sample.pdf fixture
#   - /home/user/myproject: project directory for the task
#   - /home/user/myproject/sample.pdf: pre-staged PDF containing the title
#     "Quarterly Sales Report" and a small revenue table
