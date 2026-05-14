FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install LlamaCloud Python SDKs (both the newer client and the standalone services SDK)
# plus fpdf2 (used during image build to generate a deterministic sample PDF with real tables).
RUN pip3 install --break-system-packages --no-cache-dir \
        "llama-cloud-services>=0.6.0" \
        "llama-cloud>=0.1.0" \
        "fpdf2>=2.7.0"

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="LlamaParse table-extraction task environment with a deterministic 2-page tabular PDF pre-installed."

# Create the project directory and a deterministic 2-page PDF that contains a clear
# table on each page (using fpdf2's table layout so the result is unambiguously tabular).
RUN mkdir -p /home/user/myproject && \
    python3 - <<'PYEOF'
from fpdf import FPDF

pdf = FPDF()

# ---- Page 1: Quarterly revenue table ----
pdf.add_page()
pdf.set_font("Helvetica", size=16)
pdf.cell(0, 12, "Acme Corporation - Quarterly Revenue 2024",
         new_x="LMARGIN", new_y="NEXT")
pdf.ln(2)
pdf.set_font("Helvetica", size=11)
revenue_rows = [
    ["Quarter", "Revenue", "Profit"],
    ["Q1", "$300,000", "$60,000"],
    ["Q2", "$340,000", "$82,000"],
    ["Q3", "$295,000", "$71,000"],
    ["Q4", "$315,000", "$107,000"],
]
with pdf.table() as table:
    for data_row in revenue_rows:
        row = table.row()
        for datum in data_row:
            row.cell(datum)

# ---- Page 2: Employee headcount table ----
pdf.add_page()
pdf.set_font("Helvetica", size=16)
pdf.cell(0, 12, "Acme Corporation - Employee Headcount 2024",
         new_x="LMARGIN", new_y="NEXT")
pdf.ln(2)
pdf.set_font("Helvetica", size=11)
headcount_rows = [
    ["Department", "Headcount", "Open Roles"],
    ["Engineering", "62", "8"],
    ["Sales", "34", "4"],
    ["Marketing", "18", "2"],
    ["Operations", "28", "3"],
]
with pdf.table() as table:
    for data_row in headcount_rows:
        row = table.row()
        for datum in data_row:
            row.cell(datum)

pdf.output("/home/user/myproject/quarterly_report.pdf")
PYEOF

# Container contents:
#   - Ubuntu 24.04 base with curl, wget, git, python3, pip3, pytest, bash
#   - LlamaCloud Python SDKs: llama-cloud-services, llama-cloud
#   - fpdf2 (used at build time to create the sample PDF)
#   - /home/user/myproject \u2014 project directory
#   - /home/user/myproject/quarterly_report.pdf \u2014 deterministic 2-page PDF
#     with one tabular block per page (revenue on p1, headcount on p2)
#
# The LLAMA_CLOUD_API_KEY environment variable is injected by the runtime
# (via task.toml), not baked into the image.

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
