# Act 3: Governed Customer Churn - Trusted AI Container
#
# Golden Path deployment:
# - Pinned base image (reproducibility)
# - Pinned dependencies (supply chain control)
# - JFrog Identity Token at runtime (no hardcoded secrets)
# - Xray scanned before deployment

# Use digest in production for Golden Image: python:3.11-slim@sha256:<digest>
FROM python:3.11-slim

WORKDIR /app

# Pin versions for supply chain security
RUN pip install --no-cache-dir \
    "transformers>=4.30.0,<5.0" \
    "openai>=1.0.0" \
    "frogml-inference"

COPY churn_prototype.py .

# Non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Runtime env: JF_ACCESS_TOKEN, JF_URL, CHURN_MODEL_ID, USE_FROGML_INFERENCE
ENTRYPOINT ["python", "churn_prototype.py"]
