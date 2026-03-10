#!/usr/bin/env bash
# Run tests locally with Artifactory/FrogML credentials.
# Usage: ./run-tests.sh [pytest args...]
#
# Prerequisites:
#   pip install -r requirements.txt pytest
#   (requirements pins transformers<5, numpy<2 for torch 2.2.x compatibility)
#
# Required env vars (or set in .env):
#   JF_URL           - JFrog platform URL (e.g. https://tomjfrog.jfrog.io)
#   JF_ACCESS_TOKEN - Artifactory access token (or JF_USER + JF_PASSWORD)
#   HF_ENDPOINT     - Artifactory HuggingFace repo URL
#   HF_TOKEN        - Artifactory token for model download

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Load .env if present
if [[ -f .env ]]; then
  echo "Loading .env..."
  set -a
  source .env
  set +a
fi

# Required for FrogML SDK (schema, gRPC)
: "${JF_URL:?Set JF_URL (e.g. https://tomjfrog.jfrog.io)}"
: "${JF_ACCESS_TOKEN:?Set JF_ACCESS_TOKEN (or JF_USER + JF_PASSWORD)}"

# Required for HuggingFace model download
: "${HF_ENDPOINT:?Set HF_ENDPOINT (e.g. https://YOUR_INSTANCE.jfrog.io/artifactory/api/huggingfaceml/hf-remote)}"
: "${HF_TOKEN:?Set HF_TOKEN}"

# Optional
export JF_PROJECT="${JF_PROJECT:-frogml}"

echo "JF_URL=$JF_URL"
echo "JF_PROJECT=$JF_PROJECT"
echo "HF_ENDPOINT=$HF_ENDPOINT"
echo "Running pytest..."
exec python -m pytest tests/ -v --tb=short "$@"
