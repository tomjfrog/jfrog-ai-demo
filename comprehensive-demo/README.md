# JFrog AI Comprehensive Demo - Customer Churn Prediction

A four-act technical demo transitioning a "Shadow AI" customer churn application into a governed, enterprise-ready state. Demonstrates AISecOps: treating models as versioned binaries within a single System of Record.

## Prerequisites

- **JFrog Platform** with Artifactory, Xray, AI Catalog, and JFrog ML enabled
- **Project Key** (e.g., `churn-prod`) for resource isolation and RBAC
- **frogml-cli** installed: `pip install frogml-cli` or `uv tool install frogml-cli`
- **JFrog Identity Token** with permissions for repositories and curation

### Configure frogml-cli

```bash
frogml config add \
  --url="https://<YOUR_JFROG_URL>.jfrog.io" \
  --access-token="<YOUR_IDENTITY_TOKEN>" \
  --project-key="<YOUR_PROJECT_KEY>" \
  --server-id="churn-mgmt-prod"
```

## Directory Structure

```
comprehensive-demo/
├── act1/                    # Act 1: Rogue Baseline (Shadow AI)
│   ├── churn_prototype.py   # Hardcoded keys, direct HuggingFace, pickle risk
│   ├── Dockerfile           # Unvetted base, unpinned deps
│   └── requirements.txt
├── act2/                    # Act 2: Securing the Supply Chain
│   ├── configure_proxy.sh   # HF_ENDPOINT, HF_TOKEN setup
│   └── README.md            # Artifactory proxy config steps
├── act3/                    # Act 3: Governed Trusted AI
│   ├── churn_prototype.py   # AI Gateway, frogml-inference, no pickle
│   ├── Dockerfile           # Pinned deps, non-root user
│   └── requirements.txt
├── act4/                    # Act 4: IDE Integration
│   └── README.md            # MCP plugin setup guide
├── .github/workflows/
│   └── build-and-deploy.yml # Deploy Act 3 to Artifactory
└── README.md
```

## Act Summary

| Act | Description |
|-----|-------------|
| **Act 1** | Rogue baseline: hardcoded keys, direct HuggingFace, unsafe pickle, black-box container |
| **Act 2** | Proxy config: HuggingFaceML remote, Curation, HF_ENDPOINT/HF_TOKEN |
| **Act 3** | Governed: AI Gateway, frogml-inference, versioned model, Xray-scanned container |
| **Act 4** | MCP plugin: browse AI Catalog, view Model Cards, discover alternatives in IDE |

## Implementation Comparison

| Category | Act 1: Rogue | Act 3: Governed |
|----------|--------------|-----------------|
| Credential Management | Hardcoded Third-Party API Keys | Abstracted JFrog Identity Tokens |
| Model Source | Unmanaged Public Hubs (Direct) | Curated Artifactory Proxy |
| Dependency Risk | Unscanned/Vulnerable Binaries | Xray Scanned for CVEs |
| Visibility | No Traceability (Black Box) | AI-BOM Traceability |

## Running the Demo

### Act 1 (Rogue - for comparison only)

```bash
cd act1
docker build -t churn-act1 .
echo '{"tenure_months": 8, "support_tickets": 3, "review_sentiment": "Great product!"}' | docker run -i churn-act1
```

### Act 2 (Configure proxy)

```bash
source act2/configure_proxy.sh
export HF_TOKEN="your-jfrog-identity-token"
```

### Act 3 (Governed)

```bash
cd act3
docker build -t churn-act3 .
docker run -e JF_ACCESS_TOKEN="$JF_ACCESS_TOKEN" -e JF_URL="$JF_URL" \
  -e USE_FROGML_INFERENCE=false \
  churn-act3 '{"tenure_months": 8, "support_tickets": 3, "review_sentiment": "Great product!"}'
```

## GitHub Actions Deployment

The workflow builds and deploys **Act 3 only** to Artifactory:

1. Builds Docker image from `act3/Dockerfile`
2. Pushes to Artifactory Docker repository
3. Runs Xray scan
4. Publishes build info

**Variables**: `JF_URL`, `JF_PROJECT`, `JF_DOCKER_REGISTRY` (OIDC authentication)

## License

MIT
