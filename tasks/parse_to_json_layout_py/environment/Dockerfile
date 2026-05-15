FROM ubuntu:24.04

# Install system packages, Python, and required Python libraries: the LlamaParse
# SDK (`llama-cloud-services`) for the agent's script, and `reportlab` which is
# used at image-build time to fabricate the multi-page sample PDF fixture.
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    pip3 install --break-system-packages \
        pytest-json-ctrf \
        llama-cloud-services \
        reportlab && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Standard user directory layout.
RUN mkdir -p /home/user && chmod 0755 /home/user
RUN mkdir -p /home/user/myproject

# Pre-stage a deterministic three-page Operations Manual PDF. Each page has a
# distinct top-level heading so the verifier can check that LlamaParse's JSON
# mode returned a per-page record for each one.
RUN python3 - <<'PY'
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)
from reportlab.lib import colors

styles = getSampleStyleSheet()
doc = SimpleDocTemplate("/home/user/myproject/manual.pdf", pagesize=LETTER)

story = []

# ---- Page 1: Operations Manual ----
story.append(Paragraph("Operations Manual", styles["Title"]))
story.append(Spacer(1, 18))
story.append(Paragraph(
    "This Operations Manual describes the standard procedures, equipment, and "
    "maintenance schedule for the Northbridge field station. It is intended as "
    "a reference for on-site technicians and is used here as a fixture for "
    "document parsing tests.",
    styles["BodyText"],
))
story.append(Spacer(1, 12))
story.append(Paragraph(
    "Sections in this document include an equipment list and a maintenance "
    "schedule. Each section appears on its own page.",
    styles["BodyText"],
))
story.append(PageBreak())

# ---- Page 2: Equipment List ----
story.append(Paragraph("Equipment List", styles["Title"]))
story.append(Spacer(1, 18))
story.append(Paragraph(
    "The following equipment is installed at the Northbridge field station:",
    styles["BodyText"],
))
story.append(Spacer(1, 12))
for item in [
    "Diesel generator (Model DG-450, 45 kW continuous output)",
    "Battery bank (12 x 200 Ah deep-cycle lead-acid cells)",
    "Solar array (8 x 400 W panels, fixed mount)",
    "VHF base radio (Yaesu FT-2980R)",
    "Weather instrument package (anemometer, barometer, rain gauge)",
]:
    story.append(Paragraph("&bull; " + item, styles["BodyText"]))
story.append(PageBreak())

# ---- Page 3: Maintenance Schedule ----
story.append(Paragraph("Maintenance Schedule", styles["Title"]))
story.append(Spacer(1, 18))
story.append(Paragraph(
    "Routine maintenance is performed on the following schedule. All inspections "
    "are logged in the station maintenance binder.",
    styles["BodyText"],
))
story.append(Spacer(1, 12))

schedule = [
    ["Component", "Interval", "Last Inspection"],
    ["Diesel generator", "Monthly", "2024-01-15"],
    ["Battery bank", "Quarterly", "2024-01-02"],
    ["Solar array", "Bi-annually", "2023-09-20"],
    ["VHF base radio", "Annually", "2023-11-04"],
    ["Weather instruments", "Quarterly", "2024-01-02"],
]
table = Table(schedule, hAlign="LEFT")
table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
]))
story.append(table)

doc.build(story)
PY

LABEL Author="generate-harbor-tasks"
LABEL Description="LlamaParse JSON-mode parsing task environment with the llama-cloud-services SDK and a pre-staged three-page Operations Manual PDF at /home/user/myproject/manual.pdf."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - llama-cloud-services: provides the LlamaParse Python SDK used by the task
#   - reportlab: only used at build time to generate the manual.pdf fixture
#   - /home/user/myproject: project directory for the task
#   - /home/user/myproject/manual.pdf: pre-staged three-page Operations Manual
#     with distinct page-level headings (Operations Manual, Equipment List,
#     Maintenance Schedule) used by the verifier to confirm per-page JSON output
