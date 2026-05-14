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
LABEL Description="LlamaParse multi-page PDF-to-per-page-JSON task environment with a deterministic 3-page sample PDF pre-installed."

# Create the project directory and a deterministic 3-page sample PDF.
RUN mkdir -p /home/user/myproject && \
    python3 - <<'PYEOF'
from fpdf import FPDF

pdf = FPDF()

# --- Page 1: Cover / annual report headline ---
pdf.add_page()
pdf.set_font("Helvetica", size=16)
pdf.cell(0, 12, "Acme Corporation Annual Report 2024", new_x="LMARGIN", new_y="NEXT")
pdf.ln(4)
pdf.set_font("Helvetica", size=12)
pdf.cell(0, 10, "Total Revenue: $1,250,000", new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 10, "Net Income: $320,000", new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 10, "Employees: 142", new_x="LMARGIN", new_y="NEXT")
pdf.ln(4)
pdf.multi_cell(
    0,
    8,
    (
        "Acme Corporation is pleased to share its financial performance for the year. "
        "The company achieved record growth in its services division and continued "
        "investment in research and development."
    ),
)

# --- Page 2: Quarterly breakdown ---
pdf.add_page()
pdf.set_font("Helvetica", size=16)
pdf.cell(0, 12, "Quarterly Breakdown", new_x="LMARGIN", new_y="NEXT")
pdf.ln(4)
pdf.set_font("Helvetica", size=12)
pdf.cell(0, 10, "Q1 Revenue: $260,000", new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 10, "Q2 Revenue: $300,000", new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 10, "Q3 Highlights", new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 10, "Q3 Revenue: $330,000", new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 10, "Q4 Revenue: $360,000", new_x="LMARGIN", new_y="NEXT")
pdf.ln(4)
pdf.multi_cell(
    0,
    8,
    (
        "The Q3 results reflect strong momentum in the services division, with new "
        "enterprise contracts contributing to a record quarter for Acme."
    ),
)

# --- Page 3: Outlook ---
pdf.add_page()
pdf.set_font("Helvetica", size=16)
pdf.cell(0, 12, "Outlook for 2025", new_x="LMARGIN", new_y="NEXT")
pdf.ln(4)
pdf.set_font("Helvetica", size=12)
pdf.multi_cell(
    0,
    8,
    (
        "Looking forward to 2025, Acme Corporation plans to expand into two additional "
        "markets, scale its engineering organization, and continue investing in "
        "AI-powered product capabilities. Leadership expects revenue growth of "
        "approximately 18 percent year-over-year in 2025."
    ),
)

pdf.output("/home/user/myproject/report.pdf")
PYEOF

# Container contents:
#   - Ubuntu 24.04 base with curl, wget, git, python3, pip3, pytest, bash
#   - LlamaCloud Python SDKs: llama-cloud-services, llama-cloud
#   - fpdf2 (used at build time to create the sample PDF)
#   - /home/user/myproject — project directory
#   - /home/user/myproject/report.pdf — deterministic 3-page PDF about Acme Corporation
#       Page 1: "Acme Corporation Annual Report 2024" + headline financials
#       Page 2: "Quarterly Breakdown" + "Q3 Highlights" + per-quarter figures
#       Page 3: "Outlook for 2025"
#
# The LLAMA_CLOUD_API_KEY environment variable is injected by the runtime
# (via task.toml), not baked into the image.

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
