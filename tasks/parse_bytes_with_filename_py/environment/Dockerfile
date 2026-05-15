FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    pip3 install --break-system-packages \
        pytest-json-ctrf \
        "llama-cloud-services>=0.6" \
        reportlab && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user
RUN mkdir -p /home/user/parse_bytes_task/docs

# Generate the deterministic seed PDFs used by this task.
RUN python3 - <<'PYEOF'
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

styles = getSampleStyleSheet()

specs = [
    {
        "path": "/home/user/parse_bytes_task/docs/alpha_report.pdf",
        "title": "Alpha Status Report",
        "body": [
            "This is the Alpha project's weekly status report.",
            "All milestones are on track and there are no blockers to report.",
        ],
    },
    {
        "path": "/home/user/parse_bytes_task/docs/beta_invoice.pdf",
        "title": "Beta Invoice 0001",
        "body": [
            "Bill to: ACME Holdings.",
            "One consulting engagement at a flat rate of $4,200.",
            "Total amount due: $4,200.",
        ],
    },
    {
        "path": "/home/user/parse_bytes_task/docs/gamma_memo.pdf",
        "title": "Gamma Internal Memo",
        "body": [
            "To: Engineering organization.",
            "Reminder: Please complete the annual security training by the end of the month.",
        ],
    },
]

for spec in specs:
    doc = SimpleDocTemplate(spec["path"], pagesize=LETTER, title=spec["title"])
    story = [Paragraph(spec["title"], styles["Title"]), Spacer(1, 18)]
    for paragraph in spec["body"]:
        story.append(Paragraph(paragraph, styles["BodyText"]))
        story.append(Spacer(1, 12))
    doc.build(story)
PYEOF

LABEL Author="generate-harbor-tasks"
LABEL Description="LlamaCloud LlamaParse Python task: parse PDF bytes using extra_info file_name metadata."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - llama-cloud-services (>=0.6): provides the LlamaParse client used in this task
#   - reportlab (build-time only) to generate the seeded PDFs in /home/user/parse_bytes_task/docs
#   - /home/user/parse_bytes_task: project directory for this task
#   - /home/user/parse_bytes_task/docs: seeded PDFs (alpha_report.pdf, beta_invoice.pdf, gamma_memo.pdf)
