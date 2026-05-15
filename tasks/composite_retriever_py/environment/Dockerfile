FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    pip3 install --break-system-packages \
        pytest-json-ctrf \
        requests \
        llama-cloud \
        llama-index-core \
        llama-index-indices-managed-llama-cloud && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

RUN mkdir -p /home/user/myproject/products /home/user/myproject/support && \
    cat >/home/user/myproject/products/widget_specs.txt <<'EOF'
Acme Widgets Product Specifications

Model X100 is a precision widget with a maximum operating temperature of 175 degrees Celsius.
Model X100 weighs 2.3 kilograms and has a torque rating of 42 newton-meters.
Model X200 is the heavy-duty variant; it weighs 4.7 kilograms and operates up to 220 degrees Celsius.
EOF

RUN cat >/home/user/myproject/support/faq.txt <<'EOF'
Acme Widgets Customer Support FAQ

Q: How do I reset a Model X100 widget?
A: Hold the reset button for 7 seconds while the unit is unplugged from the power source.

Q: What warranty does Acme Widgets offer?
A: All widgets come with a standard 24-month limited warranty covering manufacturing defects.
EOF

LABEL Author="generate-harbor-tasks"
LABEL Description="LlamaCloud composite-retriever task environment with the llama-index managed LlamaCloud integration and llama_cloud SDK pre-installed; includes two pre-populated document folders for products and customer support."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - LlamaCloud managed-index Python integration: llama-index-core, llama-index-indices-managed-llama-cloud
#   - llama-cloud SDK (provides CompositeRetrievalMode and related types)
#   - requests for HTTP-based verification against the LlamaCloud REST API
#   - /home/user/myproject: project directory
#   - /home/user/myproject/products/widget_specs.txt: pre-existing product specs document
#   - /home/user/myproject/support/faq.txt: pre-existing customer support FAQ document
