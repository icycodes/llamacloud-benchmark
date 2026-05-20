FROM ubuntu:24.04

# Install required apt packages, Node.js v24, and Python deps in a single layer.
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    pip3 install --break-system-packages pytest-json-ctrf requests && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Standard user home directory.
RUN mkdir -p /home/user && chmod 0755 /home/user

# Seed the project skeleton: package.json, tsconfig.json, three text documents.
RUN mkdir -p /home/user/myproject/data && \
    cat > /home/user/myproject/package.json <<'EOF'
{
  "name": "llamacloud-managed-index-ts",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "start": "tsx index.ts"
  },
  "dependencies": {
    "llamaindex": "^0.8.0"
  },
  "devDependencies": {
    "tsx": "^4.19.0",
    "typescript": "^5.5.0",
    "@types/node": "^22.0.0"
  }
}
EOF

RUN cat > /home/user/myproject/tsconfig.json <<'EOF'
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ES2022",
    "moduleResolution": "Bundler",
    "esModuleInterop": true,
    "strict": false,
    "skipLibCheck": true,
    "resolveJsonModule": true,
    "allowImportingTsExtensions": false,
    "noEmit": true
  }
}
EOF

# Three small text documents that mention the answer "Paris" so the query has grounded context.
RUN cat > /home/user/myproject/data/france.txt <<'EOF'
France is a country in Western Europe. Its capital and largest city is Paris,
which sits on the river Seine and is known for landmarks such as the Eiffel
Tower, the Louvre, and Notre-Dame Cathedral. Paris has been the political and
cultural heart of France since the medieval period.
EOF

RUN cat > /home/user/myproject/data/europe.txt <<'EOF'
Europe is a continent made up of many sovereign states. Each state has a
capital city that hosts its government. For example, the capital of Germany is
Berlin, the capital of Spain is Madrid, the capital of Italy is Rome, and the
capital of France is Paris.
EOF

RUN cat > /home/user/myproject/data/landmarks.txt <<'EOF'
The Eiffel Tower is a wrought-iron lattice tower located in Paris, France. It
was constructed for the 1889 World's Fair and remains one of the most
recognized structures in the world. Visitors to Paris frequently combine a
trip to the Eiffel Tower with a visit to the Louvre Museum.
EOF

# Install the Node.js dependencies described in package.json so the executor only writes index.ts.
RUN cd /home/user/myproject && \
    npm install --no-audit --no-fund --loglevel=error

LABEL Author="generate-harbor-tasks"
LABEL Description="LlamaCloud TypeScript managed-index task: Node.js 24 with llamaindex and tsx preinstalled, three text documents in /home/user/myproject/data, and a package.json whose 'npm start' will run the executor-supplied index.ts."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - additional pip3 packages: requests (used by tests/test_final_state.py for the LlamaCloud REST API verification)
#   - Node.js v24 for the LlamaCloud TypeScript SDK
#   - /home/user/myproject: TypeScript project skeleton with package.json, tsconfig.json
#   - /home/user/myproject/data: 3 seed text documents covering Paris/France
#   - /home/user/myproject/node_modules: llamaindex and tsx installed via npm
