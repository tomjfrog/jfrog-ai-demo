#!/bin/bash
# Act 2: Configure local workspace for secure AI sourcing via Artifactory proxy
#
# These environment variables force the transformers library to pull models
# through Artifactory, ensuring all assets are scanned before they touch
# the developer's machine.
#
# Prerequisites (configure in Artifactory first):
# 1. Create Remote Repository: HuggingFaceML package type, named hf-remote-proxy
# 2. Enable JFrog Curation for this remote repository
# 3. Define "Curation by label" policy to block malicious/non-compliant models

set -e

# Replace with your JFrog instance URL and repository name
JFROG_URL="${JFROG_URL:-https://YOUR_INSTANCE.jfrog.io}"
HF_REPO="${HF_REPO:-hf-remote-proxy}"

# Artifactory HuggingFace API endpoint
export HF_ENDPOINT="${JFROG_URL}/artifactory/api/huggingfaceml/${HF_REPO}"
export HF_TOKEN="${HF_TOKEN:-}"

# Timeouts for large model downloads through proxy
export HF_HUB_DOWNLOAD_TIMEOUT="${HF_HUB_DOWNLOAD_TIMEOUT:-86400}"
export HF_HUB_ETAG_TIMEOUT="${HF_HUB_ETAG_TIMEOUT:-86400}"

if [ -z "$HF_TOKEN" ]; then
    echo "WARNING: HF_TOKEN not set. Set it with your JFrog Identity Token:"
    echo "  export HF_TOKEN=\"your-jfrog-identity-token\""
else
    echo "Configured HuggingFace proxy: $HF_ENDPOINT"
fi
