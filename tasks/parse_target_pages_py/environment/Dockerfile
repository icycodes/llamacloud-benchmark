FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    pip3 install --break-system-packages \
        pytest-json-ctrf \
        "llama-cloud-services>=0.6" \
        "llama-parse>=0.5" \
        "pypdf>=4.0" \
        reportlab && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user
RUN mkdir -p /home/user/parse_pages_task

# Generate the deterministic five-page PDF used by this task. Each page contains
# exactly one distinct marker phrase so that the verifier can confirm which
# pages were and were not parsed by the executor's call to LlamaParse with
# `target_pages="1,3"`.
RUN python3 - <<'PYEOF'
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak

doc = SimpleDocTemplate(
    "/home/user/parse_pages_task/sample.pdf",
    pagesize=LETTER,
    title="LlamaParse target_pages Demo",
)
styles = getSampleStyleSheet()

pages = [
    ("Cover Page", "Marker-Alpha-Page-Zero", "This is the cover page of the demo report. It introduces the document and would normally be skipped when targeting only specific pages."),
    ("Background", "Marker-Bravo-Page-One", "This is the background section that describes the context of the demo report. It is one of the pages that must be parsed by the executor."),
    ("Methods", "Marker-Charlie-Page-Two", "This is the methods section. It explains how the demo data was collected and would be skipped when targeting only specific pages."),
    ("Results", "Marker-Delta-Page-Three", "This is the results section. It contains the key findings of the demo report and is one of the pages that must be parsed by the executor."),
    ("Conclusion", "Marker-Echo-Page-Four", "This is the conclusion of the demo report. It summarises the work and would be skipped when targeting only specific pages."),
]

story = []
for idx, (title, marker, body) in enumerate(pages):
    story.append(Paragraph(f"Section {idx}: {title}", styles["Title"]))
    story.append(Spacer(1, 18))
    story.append(Paragraph(marker, styles["Heading1"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(body, styles["BodyText"]))
    if idx != len(pages) - 1:
        story.append(PageBreak())

doc.build(story)
PYEOF

LABEL Author="generate-harbor-tasks"
LABEL Description="LlamaCloud LlamaParse target_pages Python task: parse only pages 1 and 3 (zero-indexed) of a seeded five-page PDF and verify the markdown output contains only the requested pages."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - LlamaParse SDKs: llama-cloud-services and llama-parse (either may be used by the executor)
#   - pypdf: used by test_initial_state.py to confirm the seeded PDF contains all five page markers
#   - reportlab (build-time only) to generate the seeded /home/user/parse_pages_task/sample.pdf
#   - /home/user/parse_pages_task: project directory for this task
#   - /home/user/parse_pages_task/sample.pdf: deterministic five-page PDF fixture with one distinct marker per page
