# Act 4: IDE Integration & Developer Experience (MCP)

## MCP Gateway Configuration

Bring the Golden Path directly into the IDE to prevent developers from bypassing security due to friction.

### 1. Install the JFrog MCP Plugin

**For Cursor or VS Code:**

1. Open Extensions (Cmd/Ctrl+Shift+X)
2. Search for "JFrog MCP" or "JFrog AI Catalog"
3. Install the JFrog MCP Gateway plugin

### 2. Authenticate

1. Open the plugin settings or command palette
2. Run: **JFrog: Configure MCP**
3. Enter:
   - **JFrog Platform URL**: `https://YOUR_INSTANCE.jfrog.io`
   - **Access Token**: Your JFrog Identity Token (from User Profile → Set Me Up → Generate Token)

### 3. Configure MCP Server

The MCP server bridges the IDE with the JFrog AI Catalog, enabling the agent to:

- Query the System of Record for approved models
- Check security status of assets
- Discover alternatives to blocked models

## Plugin Discovery Guide

### Browse the AI Catalog in the IDE

1. Open the JFrog sidebar panel (AI Catalog / MCP)
2. Browse **Registry** for approved models
3. Use **Discovery** to explore available models from supported providers

### View Security Status and Model Cards

1. Select a model in the catalog
2. View the Model Card: license, security scan results, usage
3. Evaluate alternatives when a model is blocked

### Find Vetted Internal Models

1. Switch to **Discovery** view
2. Filter by model type (Package, External, Custom)
3. Search for sentiment analysis or churn prediction models
4. Use approved models in code with confidence

## Demo Success Checklist

Verify in the JFrog ML dashboard:

- [ ] **Inference Metrics**: P50 E2E Latency and Tokens per Second for the churn endpoint
- [ ] **Inference Lake**: All model predictions and inputs logged for audit
- [ ] **Audit Trail**: AI Gateway logs show centralized tracking of external provider calls
- [ ] **Model Registry**: Churn model versioned in Artifactory with Xray scan and full AI-BOM
