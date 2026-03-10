# JFrog AI Demo - Containerized ML inference service
# Uses FrogML SDK with HuggingFace model sourced from Artifactory
#
# Build args (from GitHub vars DOCKER_REGISTRY, DOCKER_REPOSITORY, DOCKER_BASE_IMAGE):
#   DOCKER_BASE_IMAGE   - full image ref: {registry}/{repository}/{image:tag}
#
# Wheels are pre-downloaded in CI (from Artifactory) and copied into the image.
# No network access needed during Docker build.

ARG DOCKER_BASE_IMAGE=tomjfrog.jfrog.io/frogml-docker/python:3.11-slim
FROM ${DOCKER_BASE_IMAGE}

# Prevent Python from writing pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# HuggingFace/Artifactory timeouts for large model downloads
ENV HF_HUB_DOWNLOAD_TIMEOUT=86400
ENV HF_HUB_ETAG_TIMEOUT=86400

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy pre-downloaded wheels (from CI, sourced from Artifactory)
COPY wheels/ wheels/

# Copy dependency files
COPY requirements.txt .
COPY main/requirements.txt main/requirements.txt

# Install Python dependencies from local wheels (no network)
RUN pip install --no-cache-dir --no-index -f wheels/ -r requirements.txt

# Copy application code
COPY main/ main/
COPY app.py .

# Non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# HF_ENDPOINT and HF_TOKEN must be set at runtime to pull from Artifactory
# HF_MODEL_ID can override the default model
ENV PORT=8000

CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
