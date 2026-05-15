FROM ubuntu:24.04

# Install system packages, Python tooling, the managed LlamaCloud Python SDK
# (`llama-index-indices-managed-llama-cloud`), and the OpenAI LLM integration
# (`llama-index-llms-openai`) so the agent's script can build a managed index
# AND synthesize answers via the OpenAI Chat Completions API.
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    pip3 install --break-system-packages \
        pytest-json-ctrf \
        llama-index-core \
        llama-index-indices-managed-llama-cloud \
        llama-index-llms-openai && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Standard user directory layout.
RUN mkdir -p /home/user && chmod 0755 /home/user
RUN mkdir -p /home/user/myproject/docs

# Pre-stage a small, deterministic document collection so the managed index
# has predictable target text to surface in `index.as_query_engine()` source
# nodes. The "Project Aurora" file is the one whose retrieval evidence the
# verifier checks for in the `## Source Nodes` section of output.md.
RUN cat >/home/user/myproject/docs/project_aurora.txt <<'EOF'
Project Aurora is an internal research initiative at the Astrolab Foundation.

The mission of Project Aurora is to catalog every star in the Milky Way within
the next decade, combining ground-based observations with space telescope
imagery. Project Aurora's stated goals include open data sharing, reproducible
star classifications, and a public-facing star atlas.

Anyone asking "What is the mission of Project Aurora?" should be told that the
mission of Project Aurora is to catalog every star in the Milky Way.
EOF

RUN cat >/home/user/myproject/docs/company_overview.txt <<'EOF'
The Astrolab Foundation is a nonprofit research organization founded in 2008.
It funds astronomy projects, runs educational outreach programs, and partners
with universities on instrumentation research. The Foundation has no direct
connection to commercial telescope manufacturers.
EOF

RUN cat >/home/user/myproject/docs/unrelated_recipe.txt <<'EOF'
Honey Lemon Tea Recipe

Boil 250 ml of water, add one tablespoon of honey and the juice of half a
lemon, stir well, and serve hot. This recipe has nothing to do with astronomy
and is included only to give the retriever multiple candidate documents to
choose from.
EOF

LABEL Author="generate-harbor-tasks"
LABEL Description="LlamaCloud query-engine task environment: the llama-index-indices-managed-llama-cloud SDK plus the llama-index-llms-openai integration, with a pre-staged docs/ corpus including a Project Aurora document."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - llama-index-core: SimpleDirectoryReader and Document classes
#   - llama-index-indices-managed-llama-cloud: managed LlamaCloudIndex SDK
#   - llama-index-llms-openai: OpenAI LLM integration for response synthesis
#   - /home/user/myproject: project directory for the task
#   - /home/user/myproject/docs: pre-staged plain-text corpus including
#       project_aurora.txt (the target document the query engine must surface),
#       company_overview.txt and unrelated_recipe.txt (distractors)
