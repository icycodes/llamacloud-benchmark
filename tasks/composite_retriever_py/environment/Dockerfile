FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    pip3 install --break-system-packages \
        pytest-json-ctrf \
        requests \
        llama-index-core \
        llama-index-indices-managed-llama-cloud \
        llama-cloud \
        llama-cloud-services && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

# Create the project directory and seed it with the two document folders that
# the executor must turn into LlamaCloud-managed indices.
RUN mkdir -p /home/user/myproject/docs/product && \
    mkdir -p /home/user/myproject/docs/faq

RUN cat >/home/user/myproject/docs/product/streaming_api.md <<'EOF'
# Streaming API

Our streaming API delivers events over a persistent HTTPS connection using
server-sent events (SSE). The maximum payload size per event on the streaming
API is 256 KB. Messages larger than 256 KB are rejected by the gateway with
HTTP 413 Payload Too Large.

Each connection supports up to 100 concurrent subscriptions and is rate-limited
to 1000 events per minute per API key.
EOF

RUN cat >/home/user/myproject/docs/product/batch_api.md <<'EOF'
# Batch API

The batch API accepts JSON payloads up to 5 MB and returns processed results
asynchronously. Use the polling endpoint `/v1/batches/{id}` to check status.
Batch jobs that exceed 5 MB must be split into smaller chunks before submission.
EOF

RUN cat >/home/user/myproject/docs/product/webhooks.md <<'EOF'
# Webhooks

Webhooks are signed using HMAC-SHA256 with the secret configured in the
dashboard. The signature is sent in the `X-Signature` HTTP header. Webhook
deliveries are retried with exponential backoff for up to 24 hours.
EOF

RUN cat >/home/user/myproject/docs/faq/password_reset.md <<'EOF'
# How do I reset my password?

To reset your password, click the "Forgot password?" link on the sign-in page
and enter the email address associated with your account. You will receive a
password reset email within a few minutes. The reset link expires after 30
minutes. If you do not see the email, check your spam folder.

If you no longer have access to the email address on your account, contact
support to verify your identity and recover the account.
EOF

RUN cat >/home/user/myproject/docs/faq/billing.md <<'EOF'
# Billing FAQ

You can update your credit card on file by visiting Settings > Billing. We
prorate charges when you change plans mid-cycle. Invoices are emailed on the
first day of each month.
EOF

RUN cat >/home/user/myproject/docs/faq/account_deletion.md <<'EOF'
# Account deletion

To permanently delete your account, go to Settings > Account and click
"Delete account". This action is irreversible and removes all stored data
after a 14-day grace period.
EOF

LABEL Author="generate-harbor-tasks"
LABEL Description="LlamaCloud composite retriever task environment with two seeded document folders under /home/user/myproject/docs."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - LlamaCloud Python SDKs installed via pip3:
#       llama-index-core, llama-index-indices-managed-llama-cloud,
#       llama-cloud, llama-cloud-services
#   - requests for REST API verification of LlamaCloud pipelines/retrievers
#   - /home/user/myproject: project directory the executor will work in
#   - /home/user/myproject/docs/product: seed product documentation (markdown)
#   - /home/user/myproject/docs/faq: seed customer FAQ documentation (markdown)
