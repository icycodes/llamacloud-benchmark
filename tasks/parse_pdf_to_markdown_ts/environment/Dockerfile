FROM ubuntu:24.04

# Install system packages, Python (for the pytest verifier), Node.js v24
# (runtime for the TypeScript agent script), and Python `reportlab` which is
# only used at image-build time to fabricate the sample.pdf fixture.
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    pip3 install --break-system-packages \
        pytest-json-ctrf \
        reportlab && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Standard user directory layout.
RUN mkdir -p /home/user && chmod 0755 /home/user
RUN mkdir -p /home/user/myproject

# Pre-stage the sample PDF that the agent's script must parse. The PDF has a
# top-level title `Quarterly Sales Report` and a small revenue table so that
# the parsed markdown is deterministic and easy to verify.
RUN python3 - <<'PY'
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

styles = getSampleStyleSheet()
doc = SimpleDocTemplate("/home/user/myproject/sample.pdf", pagesize=LETTER)

story = []
story.append(Paragraph("Quarterly Sales Report", styles["Title"]))
story.append(Spacer(1, 18))
story.append(Paragraph(
    "This short report summarizes quarterly revenue across product lines. "
    "It is used as a test fixture for document parsing pipelines.",
    styles["BodyText"],
))
story.append(Spacer(1, 18))

data = [
    ["Product", "Q1 Revenue (USD)", "Q2 Revenue (USD)"],
    ["Widget A", "120,000", "135,500"],
    ["Widget B", "98,750", "104,300"],
    ["Service Plan", "210,000", "225,000"],
]
table = Table(data, hAlign="LEFT")
table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
]))
story.append(table)

doc.build(story)
PY

# Initialize a Node.js project in /home/user/myproject and install the
# TypeScript runner plus the official LlamaCloud TypeScript SDK so that the
# agent's `npx tsx parse_doc.ts` call works offline and `import` resolves
# locally. The `package.json` is set to ESM so top-level `await` works under
# `tsx`, matching the official LlamaParse TypeScript tutorial.
RUN cat > /home/user/myproject/package.json <<'JSON'
{
  "name": "parse-pdf-to-markdown-ts",
  "version": "1.0.0",
  "private": true,
  "type": "module"
}
JSON

RUN cd /home/user/myproject && \
    npm install --no-audit --no-fund @llamaindex/llama-cloud && \
    npm install --no-audit --no-fund --save-dev tsx typescript @types/node

LABEL Author="generate-harbor-tasks"
LABEL Description="LlamaParse PDF-to-Markdown TypeScript task environment: Ubuntu 24.04 with Node.js v24, the @llamaindex/llama-cloud SDK, the tsx TypeScript runner, and a pre-staged sample.pdf in /home/user/myproject."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - Node.js v24 from NodeSource for the TypeScript task runtime
#   - /home/user/myproject: Node project directory (ESM) for the task
#   - /home/user/myproject/package.json: pre-staged Node manifest (type=module)
#   - /home/user/myproject/node_modules/@llamaindex/llama-cloud: LlamaCloud TS SDK
#   - /home/user/myproject/node_modules/.bin/tsx: TypeScript runner
#   - /home/user/myproject/sample.pdf: pre-staged PDF containing the title
#     "Quarterly Sales Report" and a small revenue table
#   - reportlab: only used at build time to fabricate the sample.pdf fixture
