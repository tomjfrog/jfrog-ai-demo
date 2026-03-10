# Act 1: Rogue Baseline - Black Box Container
#
# This Dockerfile violates "Golden Image" principles:
# - Unvetted base image without SHA hash (no reproducibility)
# - Unpinned dependencies (supply chain drift, CVE exposure)
# - No traceability or AI-BOM
#
# Represents a "Shadow AI" deployment with zero governance.

FROM python:3.9-slim

WORKDIR /app

# Install dependencies without version pinning - supply chain risk
RUN pip install transformers openai torch

COPY churn_prototype.py .

# No non-root user, no health checks, no security scanning
ENTRYPOINT ["python", "churn_prototype.py"]
