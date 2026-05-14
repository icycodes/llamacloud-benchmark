FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages "llama-cloud>=2.1"

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="LlamaCloud incremental ingestion task environment: a project with three local files plus a prior_manifest.json that encodes one unchanged, one modified, and one deleted entry."

RUN mkdir -p /home/user/incremental_ingest/data

# Pre-existing files in /home/user/incremental_ingest/data/
RUN printf 'LlamaCloud is a managed RAG platform.\n' > /home/user/incremental_ingest/data/intro.txt && \
    printf 'RAG: Retrieval-Augmented Generation.\nEmbedding: a numeric vector that represents text.\nReranker: re-orders retrieved chunks by relevance.\n' > /home/user/incremental_ingest/data/glossary.txt && \
    printf 'v1.1.0 — added support for incremental sync planning.\n' > /home/user/incremental_ingest/data/changelog.txt

# Build the prior_manifest.json so that:
#   - intro.txt    sha256 matches the on-disk file   (UNCHANGED)
#   - glossary.txt sha256 is deliberately wrong      (MODIFIED — on-disk sha will differ)
#   - removed_doc.txt is listed but no file exists   (REMOVED)
RUN python3 - <<'PYEOF'
import hashlib
import json
import os

DATA_DIR = "/home/user/incremental_ingest/data"


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


intro_path = os.path.join(DATA_DIR, "intro.txt")
intro_sha = sha256_of(intro_path)
intro_size = os.path.getsize(intro_path)

# Deliberately stale sha256 for glossary.txt (32 zeros).
stale_glossary_sha = "0" * 64
stale_glossary_size = 1  # also stale; the script must rely on sha256, not size

# Fake entry for a file that has been deleted from disk.
removed_sha = "1" * 64
removed_size = 42

prior = {
    "files": dict(
        sorted(
            {
                "intro.txt": {"sha256": intro_sha, "size": intro_size},
                "glossary.txt": {"sha256": stale_glossary_sha, "size": stale_glossary_size},
                "removed_doc.txt": {"sha256": removed_sha, "size": removed_size},
            }.items()
        )
    )
}

with open("/home/user/incremental_ingest/prior_manifest.json", "w", encoding="utf-8") as f:
    json.dump(prior, f, indent=2)
PYEOF

# Container contents:
#   - Ubuntu 24.04 base with curl, wget, git, python3, pip, pytest, bash
#   - Python packages: llama-cloud (>=2.1) providing the LlamaCloud client class
#   - /home/user/incremental_ingest/data/intro.txt        — UNCHANGED relative to prior_manifest.json
#   - /home/user/incremental_ingest/data/glossary.txt     — MODIFIED relative to prior_manifest.json
#   - /home/user/incremental_ingest/data/changelog.txt    — NEW file, absent from prior_manifest.json
#   - /home/user/incremental_ingest/prior_manifest.json   — prior snapshot referencing intro.txt, glossary.txt, removed_doc.txt
#   - Expects LLAMA_CLOUD_API_KEY to be supplied at runtime via task.toml

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
