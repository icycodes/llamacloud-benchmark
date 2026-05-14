FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages "llama-cloud>=2.1" reportlab

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="LlamaCloud LlamaParse task environment with a sample one-page 'External References' PDF that embeds two real hyperlinks for the annotate_links feature."

RUN mkdir -p /home/user/links_task && \
    python3 - <<'PYEOF'
from reportlab.lib.pagesizes import LETTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

styles = getSampleStyleSheet()
doc = SimpleDocTemplate(
    "/home/user/links_task/references.pdf",
    pagesize=LETTER,
    title="External References",
)

elements = []
elements.append(Paragraph("External References", styles["Title"]))
elements.append(Spacer(1, 18))
elements.append(
    Paragraph(
        "This document collects two external references that downstream readers may "
        "want to follow. Each is rendered as a real PDF hyperlink so that link-aware "
        "parsers can recover the destination URL.",
        styles["BodyText"],
    )
)
elements.append(Spacer(1, 12))
elements.append(
    Paragraph(
        'For the product documentation, please '
        '<link href="https://example.com/docs" color="blue">Visit our docs</link>.',
        styles["BodyText"],
    )
)
elements.append(Spacer(1, 12))
elements.append(
    Paragraph(
        'For more about the framework, see the '
        '<link href="https://llamaindex.ai" color="blue">LlamaIndex homepage</link>.',
        styles["BodyText"],
    )
)

doc.build(elements)
PYEOF

# Container contents:
#   - Ubuntu 24.04 base with curl, wget, git, python3, pip, pytest, bash
#   - Python packages: llama-cloud (>=2.1) for the LlamaParse SDK; reportlab (build-time, for sample PDF generation)
#   - /home/user/links_task: project directory for the task
#   - /home/user/links_task/references.pdf: pre-generated single-page PDF with two real hyperlinks
#       * "Visit our docs" -> https://example.com/docs
#       * "LlamaIndex homepage" -> https://llamaindex.ai
#   - Expects LLAMA_CLOUD_API_KEY to be supplied at runtime via task.toml

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
