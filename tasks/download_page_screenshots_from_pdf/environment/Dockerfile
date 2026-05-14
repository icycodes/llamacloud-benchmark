FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install LlamaCloud Python SDKs (the agent's task uses the `llama_cloud` client),
# plus fpdf2 used at image-build time to generate a deterministic 3-page sample PDF.
RUN pip3 install --break-system-packages --no-cache-dir \
        "llama-cloud>=0.1.0" \
        "llama-cloud-services>=0.6.0" \
        "fpdf2>=2.7.0"

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="LlamaParse page-screenshot download task environment with a deterministic 3-page sample PDF pre-installed."

# Create the project directory and a deterministic 3-page PDF whose pages contain
# the section titles expected by the verifier (Alpha/Bravo/Charlie Section).
RUN mkdir -p /home/user/screenshot_task && \
    python3 - <<'PYEOF'
from fpdf import FPDF

pdf = FPDF()

# Page 1
pdf.add_page()
pdf.set_font("Helvetica", style="B", size=22)
pdf.cell(0, 14, "Alpha Section", new_x="LMARGIN", new_y="NEXT")
pdf.ln(4)
pdf.set_font("Helvetica", size=12)
pdf.multi_cell(
    0,
    8,
    (
        "This is the first section of the report. It introduces the Alpha "
        "subsystem and provides an overview of its scope, owners, and "
        "high-level milestones for the upcoming quarter."
    ),
)
pdf.ln(2)
pdf.set_font("Helvetica", style="B", size=14)
pdf.cell(0, 10, "Alpha Overview", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", size=12)
pdf.multi_cell(
    0,
    8,
    (
        "The Alpha subsystem owns ingestion and validation. Owners are the "
        "data platform team. Key deliverables include schema enforcement and "
        "deterministic intake pipelines."
    ),
)

# Page 2
pdf.add_page()
pdf.set_font("Helvetica", style="B", size=22)
pdf.cell(0, 14, "Bravo Section", new_x="LMARGIN", new_y="NEXT")
pdf.ln(4)
pdf.set_font("Helvetica", size=12)
pdf.multi_cell(
    0,
    8,
    (
        "This is the second section of the report. It describes the Bravo "
        "subsystem, which handles storage and transformation, and lists "
        "the rollout plan."
    ),
)
pdf.ln(2)
pdf.set_font("Helvetica", style="B", size=14)
pdf.cell(0, 10, "Bravo Overview", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", size=12)
pdf.multi_cell(
    0,
    8,
    (
        "The Bravo subsystem manages cold and warm storage with tiered "
        "retention policies. The transformation pipeline runs nightly and is "
        "owned by the analytics team."
    ),
)

# Page 3
pdf.add_page()
pdf.set_font("Helvetica", style="B", size=22)
pdf.cell(0, 14, "Charlie Section", new_x="LMARGIN", new_y="NEXT")
pdf.ln(4)
pdf.set_font("Helvetica", size=12)
pdf.multi_cell(
    0,
    8,
    (
        "This is the third section of the report. It covers the Charlie "
        "subsystem, which is responsible for observability and on-call "
        "coverage during incidents."
    ),
)
pdf.ln(2)
pdf.set_font("Helvetica", style="B", size=14)
pdf.cell(0, 10, "Charlie Overview", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", size=12)
pdf.multi_cell(
    0,
    8,
    (
        "Charlie consists of dashboards, alerting rules, and a 24/7 rotation. "
        "The mitigation plan includes weekly drills and a quarterly review of "
        "all open runbooks."
    ),
)

pdf.output("/home/user/screenshot_task/report.pdf")
PYEOF

# Container contents:
#   - Ubuntu 24.04 base with curl, wget, git, python3, pip3, pytest, bash
#   - LlamaCloud Python SDKs: llama-cloud (primary), llama-cloud-services
#   - fpdf2 (used at build time to create the sample PDF)
#   - /home/user/screenshot_task — project directory
#   - /home/user/screenshot_task/report.pdf — deterministic 3-page PDF with
#       page 1: "Alpha Section"
#       page 2: "Bravo Section"
#       page 3: "Charlie Section"
#
# The LLAMA_CLOUD_API_KEY environment variable is injected by the runtime
# (via task.toml), not baked into the image.

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
