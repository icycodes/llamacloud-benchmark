FROM ubuntu:24.04

# Install system packages, Python tooling, and the LlamaCloud Python SDK
# (`llama-cloud`). Both the agent's script and the verifier rely on this SDK
# to talk to the real LlamaClassify service. `reportlab` is only used at
# image-build time to fabricate the three sample PDFs.
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    pip3 install --break-system-packages \
        pytest-json-ctrf \
        llama-cloud \
        reportlab && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Standard user directory layout.
RUN mkdir -p /home/user && chmod 0755 /home/user
RUN mkdir -p /home/user/myproject/docs

# Pre-stage three deterministic sample PDFs whose content unambiguously maps to
# one of the target categories used by the LlamaClassify rules in the task.
RUN python3 - <<'PY'
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib import colors

styles = getSampleStyleSheet()

# --- invoice.pdf: an unambiguous one-page invoice -------------------------
invoice_doc = SimpleDocTemplate(
    "/home/user/myproject/docs/invoice.pdf",
    pagesize=LETTER,
)
invoice_story = [
    Paragraph("INVOICE", styles["Title"]),
    Spacer(1, 12),
    Paragraph("Invoice Number: INV-2024-0042", styles["BodyText"]),
    Paragraph("Invoice Date: 2024-03-15", styles["BodyText"]),
    Paragraph(
        "Vendor: Acme Corporation, 123 Main Street, Springfield",
        styles["BodyText"],
    ),
    Paragraph("Bill To: Globex Industries, 99 Market Ave", styles["BodyText"]),
    Spacer(1, 12),
]
invoice_table_data = [
    ["Description", "Quantity", "Unit Price (USD)", "Amount (USD)"],
    ["Widget Type A", "10", "25.00", "250.00"],
    ["Service Hours - Onsite Support", "8", "120.00", "960.00"],
    ["Annual Maintenance Plan", "1", "500.00", "500.00"],
]
invoice_table = Table(invoice_table_data, hAlign="LEFT")
invoice_table.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ]
    )
)
invoice_story.append(invoice_table)
invoice_story.append(Spacer(1, 12))
invoice_story.append(Paragraph("Subtotal: 1710.00", styles["BodyText"]))
invoice_story.append(Paragraph("Tax (8%): 136.80", styles["BodyText"]))
invoice_story.append(Paragraph("Total: 1846.80", styles["BodyText"]))
invoice_doc.build(invoice_story)

# --- receipt.pdf: a short point-of-sale receipt ---------------------------
receipt_doc = SimpleDocTemplate(
    "/home/user/myproject/docs/receipt.pdf",
    pagesize=LETTER,
)
receipt_story = [
    Paragraph("Corner Cafe", styles["Title"]),
    Paragraph("123 Elm Street, Springfield", styles["BodyText"]),
    Paragraph("RECEIPT", styles["Heading2"]),
    Paragraph("Order #: 8842    Cashier: Jamie", styles["BodyText"]),
    Paragraph("Date: 2024-03-18  Time: 09:42", styles["BodyText"]),
    Spacer(1, 12),
]
receipt_table_data = [
    ["Item", "Qty", "Price"],
    ["Latte", "1", "4.50"],
    ["Blueberry Muffin", "1", "3.25"],
]
receipt_table = Table(receipt_table_data, hAlign="LEFT")
receipt_table.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ]
    )
)
receipt_story.append(receipt_table)
receipt_story.append(Spacer(1, 12))
receipt_story.append(Paragraph("Subtotal: 7.75", styles["BodyText"]))
receipt_story.append(Paragraph("Tax: 0.60", styles["BodyText"]))
receipt_story.append(Paragraph("TOTAL: 8.35", styles["BodyText"]))
receipt_story.append(Paragraph("Paid: Visa **** 1234", styles["BodyText"]))
receipt_story.append(Paragraph("Thank you for your purchase!", styles["BodyText"]))
receipt_doc.build(receipt_story)

# --- contract.pdf: a short one-page services agreement --------------------
contract_doc = SimpleDocTemplate(
    "/home/user/myproject/docs/contract.pdf",
    pagesize=LETTER,
)
contract_story = [
    Paragraph("SERVICES AGREEMENT", styles["Title"]),
    Spacer(1, 12),
    Paragraph(
        "This Services Agreement (the \"Agreement\") is entered into as of "
        "March 20, 2024 (the \"Effective Date\") by and between Acme "
        "Corporation, a Delaware corporation (\"Provider\"), and Globex "
        "Industries, a Delaware corporation (\"Client\").",
        styles["BodyText"],
    ),
    Spacer(1, 12),
    Paragraph("1. Scope of Work", styles["Heading3"]),
    Paragraph(
        "Provider shall provide the consulting services described in "
        "Exhibit A, including software development, integration, and "
        "training services, in accordance with the timeline set forth "
        "therein.",
        styles["BodyText"],
    ),
    Paragraph("2. Term and Termination", styles["Heading3"]),
    Paragraph(
        "This Agreement shall commence on the Effective Date and continue "
        "for a term of twelve (12) months unless earlier terminated in "
        "accordance with this Section. Either party may terminate this "
        "Agreement upon thirty (30) days written notice.",
        styles["BodyText"],
    ),
    Paragraph("3. Confidentiality", styles["Heading3"]),
    Paragraph(
        "Each party agrees to keep confidential any non-public information "
        "disclosed by the other party in connection with this Agreement.",
        styles["BodyText"],
    ),
    Paragraph("4. Governing Law", styles["Heading3"]),
    Paragraph(
        "This Agreement shall be governed by and construed in accordance "
        "with the laws of the State of Delaware, without regard to its "
        "conflict-of-laws principles.",
        styles["BodyText"],
    ),
    Spacer(1, 18),
    Paragraph("IN WITNESS WHEREOF, the parties have executed this Agreement.", styles["BodyText"]),
    Spacer(1, 24),
    Paragraph("Provider: ______________________________", styles["BodyText"]),
    Paragraph("Client:   ______________________________", styles["BodyText"]),
]
contract_doc.build(contract_story)
PY

LABEL Author="generate-harbor-tasks"
LABEL Description="LlamaClassify Python task environment with the llama-cloud SDK and three pre-staged fixture PDFs (invoice/receipt/contract) under /home/user/myproject/docs."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - llama-cloud: LlamaCloud Python SDK (provides client.classifier.classify)
#   - reportlab: only used at build time to fabricate the three fixture PDFs
#   - /home/user/myproject: project directory for the task
#   - /home/user/myproject/docs/invoice.pdf: invoice fixture
#   - /home/user/myproject/docs/receipt.pdf: point-of-sale receipt fixture
#   - /home/user/myproject/docs/contract.pdf: services agreement fixture
