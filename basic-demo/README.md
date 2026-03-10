# JFrog AI Demo - Basic

Containerized sentiment classifier using FrogML SDK with a HuggingFace model sourced from Artifactory.

## Quick Start

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Configure Artifactory (replace with your instance and repo)
export HF_ENDPOINT="https://YOUR_INSTANCE.jfrog.io/artifactory/api/huggingfaceml/YOUR_HF_REPO"
export HF_TOKEN="YOUR_ARTIFACTORY_ACCESS_TOKEN"

# Run tests
pytest tests/ -v

# Run inference server
python app.py
```

## Docker

```bash
docker build -t jfrog-ai-demo:latest .
docker run -p 8000:8000 \
  -e HF_ENDPOINT="https://YOUR_INSTANCE.jfrog.io/artifactory/api/huggingfaceml/YOUR_HF_REPO" \
  -e HF_TOKEN="YOUR_ARTIFACTORY_ACCESS_TOKEN" \
  jfrog-ai-demo:latest
```

## FrogML Build

```bash
frogml config add --url=https://YOUR_INSTANCE.jfrog.io --access-token=YOUR_TOKEN
frogml models create "Sentiment Classifier" --project-key YOUR_PROJECT
frogml models build . --model-id sentiment_classifier --name v1
```
