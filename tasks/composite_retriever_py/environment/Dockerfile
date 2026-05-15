FROM ubuntu:24.04

# Install system packages, Python tooling, and the managed LlamaCloud Python
# SDK (`llama-cloud-services` re-exports `LlamaCloudIndex` and
# `LlamaCloudCompositeRetriever`; `llama-index-indices-managed-llama-cloud`
# provides the dotted import path used by the verifier).
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    pip3 install --break-system-packages \
        pytest-json-ctrf \
        llama-index-core \
        llama-cloud-services \
        llama-index-indices-managed-llama-cloud && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Standard user directory layout.
RUN mkdir -p /home/user && chmod 0755 /home/user
RUN mkdir -p /home/user/myproject/docs_astronomy /home/user/myproject/docs_cooking

# Pre-stage two small, deterministic document collections so the composite
# retriever has predictable target text to surface in each domain.
# The "Project Aurora" file is the one whose top-1 retrieval the verifier
# checks for in the astronomy section.
RUN cat >/home/user/myproject/docs_astronomy/project_aurora.txt <<'EOF'
Project Aurora is an internal research initiative at the Astrolab Foundation.

The mission of Project Aurora is to catalog every star in the Milky Way within
the next decade, combining ground-based observations with space telescope
imagery. Project Aurora's stated goals include open data sharing, reproducible
star classifications, and a public-facing star atlas.

Anyone asking "What is the mission of Project Aurora?" should be told that the
mission of Project Aurora is to catalog every star in the Milky Way.
EOF

RUN cat >/home/user/myproject/docs_astronomy/company_overview.txt <<'EOF'
The Astrolab Foundation is a nonprofit research organization founded in 2008.
It funds astronomy projects, runs educational outreach programs, and partners
with universities on instrumentation research. The Foundation has no direct
connection to commercial telescope manufacturers.
EOF

# The "Honey Lemon Tea" file is the one whose top-1 retrieval the verifier
# checks for in the cooking section.
RUN cat >/home/user/myproject/docs_cooking/honey_lemon_tea.txt <<'EOF'
Honey Lemon Tea Recipe

To make honey lemon tea, boil 250 ml of water, add one tablespoon of honey and
the juice of half a lemon, stir well, and serve hot. This soothing drink is
often consumed when fighting a cold or sore throat.

Anyone asking "How do you make Honey Lemon Tea?" should be told to boil water,
then add honey and lemon juice and stir.
EOF

RUN cat >/home/user/myproject/docs_cooking/breakfast_oats.txt <<'EOF'
Overnight Oats

Combine half a cup of rolled oats, half a cup of milk, and a spoonful of yogurt
in a jar. Refrigerate overnight, then top with fruit before serving. This file
is included only to give the retriever multiple candidate cooking documents.
EOF

LABEL Author="generate-harbor-tasks"
LABEL Description="LlamaCloud composite retriever task environment with the llama-cloud-services SDK and two pre-staged docs corpora (astronomy and cooking)."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - llama-index-core: SimpleDirectoryReader and Document classes
#   - llama-cloud-services: LlamaCloudIndex and LlamaCloudCompositeRetriever
#   - llama-index-indices-managed-llama-cloud: managed LlamaCloudIndex SDK (alias path)
#   - /home/user/myproject: project directory for the task
#   - /home/user/myproject/docs_astronomy: pre-staged astronomy corpus including
#       project_aurora.txt (target document) and company_overview.txt (distractor)
#   - /home/user/myproject/docs_cooking: pre-staged cooking corpus including
#       honey_lemon_tea.txt (target document) and breakfast_oats.txt (distractor)
