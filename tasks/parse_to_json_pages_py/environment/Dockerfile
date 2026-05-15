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
RUN mkdir -p /home/user/parse_json_task

# Generate the deterministic three-page PDF used by this task. Each page
# contains exactly one distinct marker phrase and one quarterly-revenue
# sentence so the verifier can confirm the JSON-mode parse output contains
# the correct per-page content.
RUN python3 - <<'PYEOF'
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak

doc = SimpleDocTemplate(
    "/home/user/parse_json_task/sample.pdf",
    pagesize=LETTER,
    title="LlamaParse JSON-Mode Demo",
)
styles = getSampleStyleSheet()

pages = [
    (
        "Q1 Revenue",
        "JSON-Mode-Page-One",
        "The total revenue in Q1 was $500,000.",
        "Q1 was a strong quarter for the engineering division with new contracts signed in January and March.",
    ),
    (
        "Q2 Revenue",
        "JSON-Mode-Page-Two",
        "The total revenue in Q2 was $750,000.",
        "Q2 saw revenue growth driven by an expansion of the managed services offering and renewals from existing customers.",
    ),
    (
        "Q3 Revenue",
        "JSON-Mode-Page-Three",
        "The total revenue in Q3 was $1,000,000.",
        "Q3 reached the seven-figure milestone after the new enterprise tier launched in early August.",
    ),
]

story = []
for idx, (title, marker, sentence, body) in enumerate(pages):
    story.append(Paragraph(f"Section {idx + 1}: {title}", styles["Title"]))
    story.append(Spacer(1, 18))
    story.append(Paragraph(marker, styles["Heading1"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(sentence, styles["BodyText"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(body, styles["BodyText"]))
    if idx != len(pages) - 1:
        story.append(PageBreak())

doc.build(story)
PYEOF

LABEL Author="generate-harbor-tasks"
LABEL Description="LlamaCloud LlamaParse JSON-mode Python task: parse a seeded three-page PDF with result_type='json' / get_json_result and write a structured per-page manifest."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - LlamaParse SDKs: llama-cloud-services and llama-parse (either may be used by the executor)
#   - pypdf: used by test_initial_state.py to confirm the seeded PDF contains all three page markers and quarterly amounts
#   - reportlab (build-time only) to generate the seeded /home/user/parse_json_task/sample.pdf
#   - /home/user/parse_json_task: project directory for this task
#   - /home/user/parse_json_task/sample.pdf: deterministic three-page PDF fixture with one distinct marker and quarterly revenue per page
