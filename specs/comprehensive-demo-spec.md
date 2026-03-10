Technical Specification: JFrog AI Demo (Customer Churn Prediction)

1. SPECIFICATION CONTEXT & ENVIRONMENT SETUP

Objective

This technical specification outlines the transition of a "Shadow AI" customer churn application into a governed, enterprise-ready state. In many organizations, AI is currently treated as "magic"—isolated experiments running as black boxes. To future-proof the AI-native enterprise, we must shift to an AISecOps discipline: treating models as versioned binaries within a single System of Record. This demo establishes a secure software supply chain where AI assets are scanned, versioned, and managed alongside traditional software binaries.

Ground Truths and Prerequisites

To execute this demo, ensure the following prerequisites from the JFrog Platform are available:

* Platform Access: A JFrog instance with Artifactory, Xray, AI Catalog, and JFrog ML enabled.
* Project Infrastructure: A dedicated Project Key (e.g., churn-prod) to enable resource isolation and RBAC.
* CLI Installation: To ensure a clean, globally accessible developer environment, install the frogml-cli using the recommended method:
* Identity Token: A valid JFrog Identity Token with appropriate permissions to configure repositories and curation policies.

User Configuration Command

Senior Architects utilize server-id tags to manage multiple environments (Dev, Staging, Prod). Use the following command to initialize the CLI:

# Configure the environment with a unique server-id for environment management
frogml config add \
  --url="https://<YOUR_JFROG_URL>.jfrog.io" \
  --access-token="<YOUR_IDENTITY_TOKEN>" \
  --project-key="<YOUR_PROJECT_KEY>" \
  --server-id="churn-mgmt-prod"



--------------------------------------------------------------------------------


2. ACT 1: THE "ROGUE" BASELINE (SHADOW AI DETECTION)

Application Logic Prompt

Act 1 represents the "Wild West" state of AI. This implementation relies on unvetted external calls and "magical" black-box models that bypass security gates.

Prompt for Claude Code:

Generate a Python script named churn_prototype.py that predicts customer churn.

1. Include a hardcoded variable OPENAI_API_KEY = "sk-shadow-ai-key-secret-12345" for sentiment analysis of reviews using direct OpenAI API calls.
2. Use the transformers library to directly download the distilbert-base-uncased model from the public Hugging Face Hub.
3. Critical: Include logic that attempts to load a .pkl (pickle) file for model weights, representing the risk of unsafe serialization attacks highlighted in the Rami Pinku blog.
4. Implement a dummy prediction function that processes a feature vector and prints the results.

Containerization Prompt

To demonstrate the governance gap, we bundle this script into an unmanaged container.

Prompt for Claude Code:

Create a Dockerfile for the churn_prototype.py application.

1. Use an unvetted base image (e.g., python:3.9-slim) without a specific SHA hash, violating "Golden Image" principles.
2. Install dependencies (transformers, openai, torch) via standard pip without pinning versions.
3. Copy the script and set it as the entry point.
4. Add a comment explaining that this container represents a "Black Box" deployment with no traceability or AI-BOM.

Risk Documentation

The current state of "Act 1" presents severe operational liabilities:

* The Security Threat: AI models are executable code. While the total number of models on public hubs grew 3x recently, malicious models grew 7x. Unvetted .pkl or .safetensors files are potential time bombs for system compromise.
* The Governance Gap: 7 out of 10 personnel use AI through personal accounts, and 4 out of 10 enter sensitive data into unmanaged assistants. Hardcoded keys in Act 1 allow for massive data leakage with zero oversight.
* The Visibility Blind Spot: This application is invisible to the enterprise. Without an AI-BOM, security cannot answer "Where is this model running?" or "Who approved this binary?"


--------------------------------------------------------------------------------


3. ACT 2: SECURING THE SUPPLY CHAIN (ARTIFACTORY & CURATION)

Proxy Configuration Prompt

We establish a "Golden Path" by redirecting external traffic through a managed proxy in Artifactory.

Prompt for Claude Code:

Provide step-by-step instructions to configure the JFrog Platform for secure AI sourcing:

1. Create a Remote Repository in Artifactory using the HuggingFaceML package type named hf-remote-proxy.
2. Enable JFrog Curation for this remote repository.
3. Define a "Curation by label" policy to block models flagged as malicious or having non-compliant licenses (e.g., blocking models without verified commercial licenses) directly at the cache level.

Dependency Redirection Prompt

Developers must be redirected from the public internet to the secure internal proxy.

Prompt for Claude Code:

Generate shell commands to configure the local workspace environment variables:

1. Set HF_ENDPOINT to point to the hf-remote-proxy URL in Artifactory.
2. Set HF_TOKEN to the JFrog Identity Token.
3. Explain that these variables force the transformers library to pull models through Artifactory, ensuring all assets are scanned before they touch the developer's machine.

Policy Enforcement Analysis

By centralizing traffic, we distinguish between two critical enforcement points:

* Curation by Label: This applies to the Remote Repository. It prevents unvetted or malicious models from being cached from the public hub (e.g., Hugging Face).
* Xray Download Block: This applies to the Local Repository. It ensures that even if a model exists internally, it cannot be used in a build if a new CVE is discovered. This transition transforms Shadow AI into a visible inventory tracked within the Detected Models dashboard in the AI Catalog.


--------------------------------------------------------------------------------


4. ACT 3: OPERATIONALIZING TRUSTED AI (AI GATEWAY & FROGML SDK)

AI Gateway Refactoring Prompt

The application must eliminate hardcoded secrets and use the secure JFrog AI Gateway.

Prompt for Claude Code:

Refactor the sentiment analysis in churn_prototype.py to use the JFrog AI Gateway:

1. Replace the raw OpenAI client initialization.
2. Set the base_url to the JFrog Platform's AI Gateway endpoint (e.g., https://<YOUR_URL>/artifactory/api/ai/api/v1).
3. Replace the hardcoded secret with a JFrog Identity Token.
4. Ensure the model parameter uses the approved naming convention from the JFrog AI Catalog.

Inference SDK Implementation Prompt

Migrate churn prediction to a managed, versioned inference service using the frogml-inference SDK.

Prompt for Claude Code:

Modify the churn prediction logic in churn_prototype.py:

1. Add the specific import: from frogml_inference.realtime_client import RealTimeClient.
2. Initialize the RealTimeClient using a managed model_id (e.g., churn-prediction-v1).
3. Replace the local feature extraction logic with client.predict(feature_vector), demonstrating how the model is now a versioned binary served from a secure Data Plane.

Verification Table: Implementation Comparison

Category	Act 1: Rogue (Shadow AI)	Act 3: Governed (Trusted AI)
Credential Management	Hardcoded Third-Party API Keys	Abstracted JFrog Identity Tokens
Model Source	Unmanaged Public Hubs (Direct)	Curated Artifactory Proxy (Golden Path)
Dependency Risk	Unscanned/Vulnerable Binaries	Xray Scanned for CVEs and Malicious Code
Visibility	No Traceability (Black Box)	AI-BOM (AI Bill of Materials) Traceability


--------------------------------------------------------------------------------


5. ACT 4: IDE INTEGRATION & DEVELOPER EXPERIENCE (MCP)

MCP Gateway Configuration Prompt

To prevent "developer friction"—where developers bypass security because it's too difficult—we bring the Golden Path directly into the IDE.

Prompt for Claude Code:

Document the setup for the JFrog MCP Gateway plugin for Cursor or VS Code:

1. Install the JFrog MCP plugin to allow the IDE agent to query the System of Record.
2. Authenticate using the JFrog Platform URL and an Access Token.
3. Configure the MCP server to bridge the IDE with the JFrog AI Catalog.

Plugin Discovery Prompt

Enable developers to find secure alternatives to blocked assets without leaving their code.

Prompt for Claude Code:

Provide a guide for a developer to use the IDE plugin to:

1. Browse the AI Catalog for approved models directly in the sidebar.
2. View security status and "Model Cards" within the IDE to evaluate alternatives to blocked models.
3. Use the Discovery features to find vetted, internal custom models for sentiment analysis.

Final Verification: Demo Success Checklist

Evidence of a successful deployment is found in the JFrog ML dashboard:

* [ ] Inference Metrics: Verify the dashboard displays P50 E2E Latency and Tokens per Second for the churn endpoint.
* [ ] Inference Lake: Confirm all model predictions and inputs are being logged in the Inference Lake for audit-ready evidence.
* [ ] Audit Trail: Verify the AI Gateway logs show centralized tracking of all external provider calls.
* [ ] Model Registry: Confirm the churn model is versioned in Artifactory with an associated Xray scan and a full AI-BOM.


--------------------------------------------------------------------------------


6. MANDATORY FORMATTING & CONSTRAINTS

* No Diagrams: This document contains zero Mermaid, SVG, or interactive widgets.
* Header Structure: All sections utilize Markdown H2 and H3 headers.
* Code Identifiers: Every code block uses explicit language identifiers:
  * bash for CLI and environment commands.
  * python for SDK and logic implementation.
* Language: The document is written entirely in English.
