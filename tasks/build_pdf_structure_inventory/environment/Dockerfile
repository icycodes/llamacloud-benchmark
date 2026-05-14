FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install LlamaCloud Python SDKs (both the newer client and the standalone services SDK)
# plus fpdf2 (used during image build to generate a deterministic multi-page sample PDF).
RUN pip3 install --break-system-packages --no-cache-dir \
        "llama-cloud-services>=0.6.0" \
        "llama-cloud>=0.1.0" \
        "fpdf2>=2.7.0"

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="LlamaParse structure-inventory task environment with a deterministic 3-page sample PDF pre-installed."

# Create the project directory and a deterministic 3-page PDF whose page i contains
# the section title that the verifier expects on page i.
RUN mkdir -p /home/user/myproject && \
    python3 - <<'PYEOF'
from fpdf import FPDF

pdf = FPDF()

# Page 1
pdf.add_page()
pdf.set_font("Helvetica", style="B", size=22)
pdf.cell(0, 14, "Project Phoenix Overview", new_x="LMARGIN", new_y="NEXT")
pdf.ln(4)
pdf.set_font("Helvetica", size=12)
pdf.multi_cell(
    0,
    8,
    (
        "The Phoenix Initiative is a multi-quarter program aimed at modernizing "
        "the company's data infrastructure. This overview describes the program's "
        "scope, expected outcomes, and stakeholders."
    ),
)
pdf.ln(2)
pdf.set_font("Helvetica", style="B", size=14)
pdf.cell(0, 10, "Scope", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", size=12)
pdf.multi_cell(
    0,
    8,
    (
        "The Phoenix Initiative covers ingestion, storage, transformation, and "
        "observability layers. Each layer has dedicated owners and quarterly "
        "delivery checkpoints."
    ),
)

# Page 2
pdf.add_page()
pdf.set_font("Helvetica", style="B", size=22)
pdf.cell(0, 14, "Implementation Roadmap", new_x="LMARGIN", new_y="NEXT")
pdf.ln(4)
pdf.set_font("Helvetica", size=12)
pdf.multi_cell(
    0,
    8,
    (
        "The roadmap is organized into four quarters with explicit milestones. "
        "Each milestone has acceptance criteria, owners, and an associated risk "
        "register entry."
    ),
)
pdf.ln(2)
pdf.set_font("Helvetica", style="B", size=14)
pdf.cell(0, 10, "Milestones", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", size=12)
pdf.multi_cell(
    0,
    8,
    (
        "Q1 milestones focus on ingestion. Q2 milestones focus on storage. "
        "Q3 milestones focus on transformation. Q4 milestones focus on "
        "observability and rollout."
    ),
)

# Page 3
pdf.add_page()
pdf.set_font("Helvetica", style="B", size=22)
pdf.cell(0, 14, "Risk Assessment Summary", new_x="LMARGIN", new_y="NEXT")
pdf.ln(4)
pdf.set_font("Helvetica", size=12)
pdf.multi_cell(
    0,
    8,
    (
        "This section summarizes the major risks identified across the program. "
        "Each risk is rated by probability and impact, and is linked to one or "
        "more mitigation actions."
    ),
)
pdf.ln(2)
pdf.set_font("Helvetica", style="B", size=14)
pdf.cell(0, 10, "Mitigation Plan", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", size=12)
pdf.multi_cell(
    0,
    8,
    (
        "Mitigation actions include dual-vendor sourcing for ingestion, weekly "
        "backup drills for storage, regression test coverage for transformation, "
        "and on-call coverage for observability."
    ),
)

pdf.output("/home/user/myproject/report.pdf")
PYEOF

# Container contents:
#   - Ubuntu 24.04 base with curl, wget, git, python3, pip3, pytest, bash
#   - LlamaCloud Python SDKs: llama-cloud-services, llama-cloud
#   - fpdf2 (used at build time to create the sample PDF)
#   - /home/user/myproject - project directory
#   - /home/user/myproject/report.pdf - deterministic 3-page PDF with
#       page 1: "Project Phoenix Overview" (mentions "Phoenix Initiative")
#       page 2: "Implementation Roadmap" (mentions "milestones")
#       page 3: "Risk Assessment Summary" (mentions "Mitigation")
#
# The LLAMA_CLOUD_API_KEY environment variable is injected by the runtime
# (via task.toml), not baked into the image.

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
