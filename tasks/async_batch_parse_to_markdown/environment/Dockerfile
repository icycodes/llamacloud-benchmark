FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages "llama-cloud>=2.1" reportlab

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="LlamaCloud LlamaParse async batch parsing task environment with three single-page sample PDFs (Alpha/Bravo/Charlie Project Reports) pre-generated under /home/user/batch_parse/pdfs."

RUN mkdir -p /home/user/batch_parse/pdfs && \
    python3 - <<'PYEOF'
from reportlab.lib.pagesizes import LETTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

styles = getSampleStyleSheet()

REPORTS = [
    ("alpha.pdf",   "Alpha Project Report",   "Widget"),
    ("bravo.pdf",   "Bravo Project Report",   "Gadget"),
    ("charlie.pdf", "Charlie Project Report", "Sprocket"),
]

for filename, title, product in REPORTS:
    doc = SimpleDocTemplate(
        f"/home/user/batch_parse/pdfs/{filename}",
        pagesize=LETTER,
        title=title,
    )
    elements = [
        Paragraph(title, styles["Title"]),
        Spacer(1, 18),
        Paragraph(
            f"This document is the official {title}. "
            f"It describes the development progress of the {product} product line "
            "during the reporting period and is used for the LlamaParse batch parsing benchmark.",
            styles["BodyText"],
        ),
        Spacer(1, 12),
        Paragraph(
            f"Key milestone: the {product} team shipped the new release on schedule "
            "and met every quality target defined in the project charter.",
            styles["BodyText"],
        ),
    ]
    doc.build(elements)
PYEOF

# Container contents:
#   - Ubuntu 24.04 base with curl, wget, git, python3, pip, pytest, bash
#   - Python packages: llama-cloud (>=2.1) for the LlamaCloud SDK (provides AsyncLlamaCloud);
#     reportlab (build-time only, used to pre-generate the sample PDFs)
#   - /home/user/batch_parse: project directory for the task
#   - /home/user/batch_parse/pdfs/alpha.pdf, bravo.pdf, charlie.pdf:
#     three single-page sample PDFs with distinct titles
#     ("Alpha Project Report", "Bravo Project Report", "Charlie Project Report")
#   - Expects LLAMA_CLOUD_API_KEY to be supplied at runtime via task.toml

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
