# JFrog AI Demo

A technical demo showcasing JFrog's AI/ML capabilities. This project includes two complementary approaches that coexist in the same repository.

## Demo Approaches

| Approach | Description | Use Case |
|----------|-------------|----------|
| **Basic** | Containerized sentiment classifier using FrogML SDK with a HuggingFace model sourced from Artifactory. Focuses on the fundamentals: model loading via proxy, Docker deployment, and Xray scanning. | Quick start, learning the core JFrog ML workflow |
| **Advanced** | Four-act narrative transitioning "Shadow AI" to governed AISecOps. Covers rogue baseline (Act 1), supply chain security (Act 2), AI Gateway + frogml-inference (Act 3), and IDE/MCP integration (Act 4). | Enterprise readiness, security governance, full AISecOps story |
| **Notebooks** | Jupyter notebook demos: sentiment from Artifactory, FrogML log_model (AI-BOM), HuggingFace proxy comparison | Interactive exploration, learning |

Both demos deploy to Artifactory and are scanned for security and license compliance via JFrog Xray.

---

## Basic Demo

The basic demo is a containerized Python ML application using the FrogML SDK with a HuggingFace model sourced from Artifactory.

### Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  HuggingFace    │────▶│   Artifactory    │────▶│  Python App     │
│  (upstream)     │     │  HuggingFaceML   │     │  (FrogML SDK)   │
└─────────────────┘     │  remote repo     │     └────────┬────────┘
                        └──────────────────┘              │
                                                          ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  PyPI           │────▶│   Artifactory    │────▶│  CI Pipeline    │
│  (upstream)     │     │  PyPI remote     │     │  1. pip download │
└─────────────────┘     └──────────────────┘     │  2. tests       │
                                                  │  3. Docker build│
                        ┌──────────────────┐     │  4. push zip    │
                        │   Artifactory    │◀────└─────────────────┘
                        │   Docker + zip   │
                        │   (Xray scanned) │
                        └──────────────────┘
```

### Build Pipeline (Option A: Download Once, Reuse)

Dependencies are downloaded **once** from Artifactory and reused for both tests and the Docker image:

1. **Configure pip** — OIDC credentials configure pip to pull from Artifactory PyPI
2. **Download wheels** — `pip download` fetches all dependencies to `basic-demo/wheels/`
3. **Run tests** — `pip install --no-index -f wheels/` (no network)
4. **Docker build** — `COPY wheels/` and `pip install --no-index` (no network)
5. **Publish** — Docker image and zip (app + wheels) to Artifactory

This avoids double downloads and keeps the Docker build offline.

## Prerequisites

- **Python 3.11+**
- **JFrog Artifactory** with:
  - A HuggingFace remote repository (or HuggingFaceML package type) caching models from HuggingFace
  - A PyPI remote (or virtual) repository for Python dependencies
  - A Docker local repository for container images and base images
  - A generic local repository for the Python app archive (app + wheels)
  - **JFrog Xray** for security and license scanning (optional but recommended)

## Project Structure

```
jfrog-ai-demo/
├── basic-demo/              # Basic: FrogML sentiment classifier
│   ├── main/
│   │   ├── __init__.py
│   │   ├── model.py
│   │   └── requirements.txt
│   ├── tests/
│   │   └── ut/
│   │       └── test_model.py
│   ├── app.py               # FastAPI inference server
│   ├── requirements.txt
│   ├── Dockerfile
│   └── README.md
├── comprehensive-demo/      # Advanced: 4-act AISecOps narrative
│   ├── act1/                # Rogue baseline (Shadow AI)
│   ├── act2/                # Proxy config (Artifactory & Curation)
│   ├── act3/                # Governed (AI Gateway, frogml-inference)
│   └── act4/                # IDE/MCP integration docs
├── notebooks/               # Jupyter demo scenarios
│   ├── sentiment/           # HuggingFace/transformers demos
│   │   ├── 01-sentiment-from-artifactory.ipynb
│   │   ├── 02-frogml-log-model-ai-bom.ipynb
│   │   └── 03-huggingface-proxy-demo.ipynb
│   └── fraud-detection/     # CatBoost/XGBoost fraud model (conda.yml)
│       ├── credit-card-fraud-detection.ipynb
│       └── main/
├── .github/
│   └── workflows/
│       ├── build-and-deploy.yml              # Basic: sentiment classifier
│       ├── comprehensive-build-and-deploy.yml # Advanced: Act 3 churn prediction
│       └── notebooks-execute.yml             # Execute notebooks (CI verification)
├── specs/
│   └── comprehensive-demo-spec.md
└── README.md
```

## Quick Start

### 1. Configure Artifactory for HuggingFace Models

1. In Artifactory, create a **remote repository** of type **HuggingFaceML** pointing to `https://huggingface.co`
2. Enable **Curation** in Administration → Curation Settings if using AI Catalog
3. Allow your target model (e.g. `distilbert-base-uncased-finetuned-sst-2-english`) in the AI Catalog if applicable

### 2. Local Development

```bash
cd basic-demo

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Point to Artifactory HuggingFace repo (replace with your instance and repo)
export HF_ENDPOINT="https://YOUR_INSTANCE.jfrog.io/artifactory/api/huggingfaceml/YOUR_HF_REPO"
export HF_TOKEN="YOUR_ARTIFACTORY_ACCESS_TOKEN"

# Run tests
pytest tests/ -v

# Run inference server locally
python app.py
```

Then call the API:

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "This product is amazing!"}'
```

### 3. Docker Build and Run

**CI pipeline:** The GitHub Actions workflow downloads wheels from Artifactory, runs tests, and builds the Docker image. No network access is needed during the Docker build.

**Local build:** You must download wheels first (with pip configured for Artifactory), then build:

```bash
cd basic-demo

# Download wheels (requires pip configured for Artifactory)
pip download -r requirements.txt -d wheels

# Build (uses local wheels, no network)
docker build -t jfrog-ai-demo:latest .

# Run (pass Artifactory credentials to pull model)
docker run -p 8000:8000 \
  -e HF_ENDPOINT="https://YOUR_INSTANCE.jfrog.io/artifactory/api/huggingfaceml/YOUR_HF_REPO" \
  -e HF_TOKEN="YOUR_ARTIFACTORY_ACCESS_TOKEN" \
  jfrog-ai-demo:latest
```

### 4. FrogML Build (JFrog ML Platform)

If using JFrog ML for model builds and deployment:

```bash
cd basic-demo

# Install FrogML CLI
pip install frogml-cli

# Configure
frogml config add --url=https://YOUR_INSTANCE.jfrog.io --access-token=YOUR_TOKEN

# Create model and build
frogml models create "Sentiment Classifier" --project-key YOUR_PROJECT
frogml models build . --model-id sentiment_classifier --name v1
```

## GitHub Actions Deployment

### Basic Demo

The workflow in `.github/workflows/build-and-deploy.yml` builds and deploys the sentiment classifier from `basic-demo/` (runs on changes to `basic-demo/**`):

1. Configures pip for Artifactory (OIDC)
2. Downloads Python wheels once from Artifactory PyPI
3. Runs unit tests using local wheels (`--no-index`)
4. Builds the Docker image using pre-downloaded wheels (no network)
5. Pushes the image to Artifactory (on `main`/`master`)
6. Scans the image with JFrog Xray
7. Creates a zip of the app + wheels and uploads to a generic Artifactory repo
8. Publishes build info for Xray scanning

### GitHub Repository Variables

Workflows use [jfrog/setup-jfrog-cli@v4](https://github.com/jfrog/setup-jfrog-cli) with OIDC for authentication. Configure a GitHub OIDC integration in your JFrog platform (`github-oidc-integration` / `jfrog-github`).

See [Repository Variables Checklist](#repository-variables-checklist) below for the full list.

### Advanced Demo

The workflow in `.github/workflows/comprehensive-build-and-deploy.yml` builds and deploys Act 3 (governed churn prediction) to Artifactory. It runs on push/PR when files under `comprehensive-demo/` change.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `HF_ENDPOINT` | Artifactory HuggingFace API URL (required for Artifactory-sourced models) |
| `HF_TOKEN` | Artifactory access token for HuggingFace repo |
| `HF_MODEL_ID` | Model name (default: `distilbert-base-uncased-finetuned-sst-2-english`) |
| `HF_HUB_DOWNLOAD_TIMEOUT` | Download timeout in seconds (default: 86400) |
| `HF_HUB_ETAG_TIMEOUT` | ETag timeout (default: 86400) |

## Security and License Scanning

- **Docker image**: Scanned via `jf docker scan` in the GitHub Actions workflow
- **Python app zip**: Included in build info; Xray scans when build is published
- Ensure Xray is configured with appropriate policies and indexed repositories

---

## Repository Variables Checklist

Configure these **GitHub repository variables** (Settings → Secrets and variables → Actions → Variables):

| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| `JF_URL` | Yes | `https://tomjfrog.jfrog.io` | JFrog platform URL |
| `JF_PROJECT` | Yes | `my-project` | JFrog project key |
| `DOCKER_REGISTRY` | Yes | `tomjfrog.jfrog.io` | Docker registry host (no `https://`) |
| `DOCKER_REPOSITORY` | Yes | `frogml-docker` | Base image repository path |
| `DOCKER_BASE_IMAGE` | Yes | `python3.11-slim:3.11-slim` | Base image name and tag |
| `ARTIFACTORY_DOCKER_REPO` | No | `docker-local` | Docker repo for built image (default: `docker-local`) |
| `ARTIFACTORY_GENERIC_REPO` | No | `generic-local` | Generic repo for app zip (default: `generic-local`) |
| `JF_PYPI_REPO` | No | `pypi-virtual` | PyPI virtual repo for pip (default: `pypi-virtual`) |
| `ARTIFACTORY_HF_REPO` | No | `hf-remote` | HuggingFaceML repo for model download (default: `hf-remote`) |

**Prerequisites:** Base image must exist in Artifactory at `{DOCKER_REGISTRY}/{DOCKER_REPOSITORY}/{DOCKER_BASE_IMAGE}`. Push `python:3.11-slim` into your Docker repo if needed.

---

## Advanced Demo

The **comprehensive-demo** directory contains a four-act narrative that transitions a "Shadow AI" customer churn application into a governed, enterprise-ready state. It demonstrates AISecOps: treating models as versioned binaries within a single System of Record.

| Act | Contents |
|-----|----------|
| **Act 1** | Rogue baseline: hardcoded API keys, direct HuggingFace, unsafe pickle, black-box container |
| **Act 2** | Proxy configuration: HuggingFaceML remote, Curation policies, HF_ENDPOINT/HF_TOKEN setup |
| **Act 3** | Governed: JFrog AI Gateway, frogml-inference RealTimeClient, versioned model, Xray-scanned container |
| **Act 4** | IDE integration: MCP plugin setup, AI Catalog browsing, Model Cards |

**Quick start:**

```bash
cd comprehensive-demo
# See comprehensive-demo/README.md for full instructions
```

**Workflows:** All demos have dedicated GitHub Actions workflows:
- `build-and-deploy.yml` — Basic demo (sentiment classifier; runs on changes to `basic-demo/**`)
- `comprehensive-build-and-deploy.yml` — Advanced demo (Act 3 churn prediction; runs on changes to `comprehensive-demo/**`)
- `notebooks-execute.yml` — Execute Jupyter notebooks (runs on changes to `notebooks/**`)

---

## Notebooks

The **notebooks/** directory contains scenario-based demos. Each scenario has its own env config (Conda and/or pip).

| Scenario | Description |
|----------|-------------|
| **sentiment/** | HuggingFace sentiment model, FrogML log_model, proxy demo |
| **fraud-detection/** | CatBoost/XGBoost credit card fraud (Conda recommended) |

**Quick start (sentiment):**

```bash
pip install -r notebooks/requirements.txt
cd notebooks/sentiment
jupyter notebook
```

**Quick start (fraud-detection):**

```bash
cd notebooks/fraud-detection
conda env create -f conda.yml
conda activate fraud-detection
jupyter notebook
```

See [notebooks/README.md](notebooks/README.md) for full setup and Conda details.

## License

MIT
