FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    pip3 install --break-system-packages pytest-json-ctrf requests && \
    npm i -g tsx typescript && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

# Initialize project directory with the LlamaCloud Client SDK pre-installed,
# plus sample data files for the two indices the task must build.
RUN mkdir -p /home/user/composite_retriever && \
    cd /home/user/composite_retriever && \
    npm init -y >/dev/null && \
    npm pkg set type="module" >/dev/null && \
    npm install --silent @llamaindex/llama-cloud@latest && \
    npm install --silent --save-dev typescript@latest tsx@latest @types/node@latest && \
    mkdir -p /home/user/composite_retriever/data/policies && \
    mkdir -p /home/user/composite_retriever/data/faq

RUN cat >/home/user/composite_retriever/data/policies/refund_policy.txt <<'EOF'
Refund Policy
=============

ACME Corp offers a 30-day money-back guarantee on all software subscriptions.
To request a refund, customers must contact billing@acme.example within 30
calendar days of their original purchase date. Refunds are processed back to
the original payment method within 5-7 business days. Annual plans are
prorated for refunds after the first 30 days.
EOF

RUN cat >/home/user/composite_retriever/data/policies/security_policy.txt <<'EOF'
Information Security Policy
===========================

All customer data is encrypted at rest using AES-256 and in transit using
TLS 1.3. Employees must use multi-factor authentication for all internal
systems. Access to production data is granted on a least-privilege basis and
reviewed quarterly. Security incidents must be reported to the CISO within
one hour of detection.
EOF

RUN cat >/home/user/composite_retriever/data/policies/leave_policy.txt <<'EOF'
Leave Policy
============

Full-time employees accrue 20 paid time off (PTO) days per year, plus 10
paid public holidays. PTO requests should be submitted at least two weeks in
advance through the HR portal. Unused PTO can be carried over up to a
maximum of 5 days into the next calendar year.
EOF

RUN cat >/home/user/composite_retriever/data/faq/billing_faq.txt <<'EOF'
Billing FAQ
===========

Q: How do I update my credit card on file?
A: Sign in to your account, go to Settings -> Billing, and click "Update
   Payment Method". Changes take effect immediately.

Q: When am I charged for my subscription?
A: Subscriptions renew on the first of every month for monthly plans, or on
   the anniversary of the purchase date for annual plans.

Q: Can I get an invoice for my purchase?
A: Yes. Invoices are automatically emailed after each successful payment.
   You can also download invoices from Settings -> Billing -> Invoices.
EOF

RUN cat >/home/user/composite_retriever/data/faq/product_faq.txt <<'EOF'
Product FAQ
===========

Q: Which operating systems are supported?
A: The desktop client supports Windows 10+, macOS 12+, and Ubuntu 22.04+.

Q: Is there an API rate limit?
A: Yes. The default rate limit is 100 requests per minute per API key.
   Higher limits are available on enterprise plans.

Q: How do I reset my password?
A: Visit https://acme.example/reset-password and follow the email link.
EOF

LABEL Author="generate-harbor-tasks"
LABEL Description="LlamaCloud composite retriever TypeScript task environment with @llamaindex/llama-cloud SDK preinstalled."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - extra pip3 package: requests (used by tests/test_final_state.py to call the LlamaCloud REST API)
#   - Node.js v24 with global tsx and typescript for TypeScript execution
#   - /home/user/composite_retriever: project directory
#       * package.json with @llamaindex/llama-cloud, tsx, typescript, @types/node installed
#       * data/policies/*.txt and data/faq/*.txt sample content files
