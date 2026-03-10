# Act 2: Securing the Supply Chain (Artifactory & Curation)

## Proxy Configuration Steps

### 1. Create Remote Repository in Artifactory

1. Navigate to **Administration** → **Repositories** → **Repositories**
2. Click **Add Repositories** → **Remote Repository**
3. Set **Package Type** to **HuggingFaceML**
4. Set **Repository Key** to `hf-remote-proxy`
5. Set **URL** to `https://huggingface.co`
6. Save

### 2. Enable JFrog Curation

1. Navigate to **Administration** → **Curation Settings** → **General**
2. Toggle **Curation On** to ON
3. Click **Enable repositories** and ensure `hf-remote-proxy` is enabled
4. Verify **HuggingFaceML** package type is toggled ON

### 3. Define Curation by Label Policy

1. Navigate to **Curation Settings** → **Policies**
2. Create a policy to block models flagged as:
   - Malicious
   - Non-compliant licenses (e.g., no verified commercial license)
3. Apply at the remote repository cache level

### 4. Configure Local Workspace

Run the configuration script:

```bash
source act2/configure_proxy.sh
export HF_TOKEN="your-jfrog-identity-token"
```

Or set manually:

```bash
export HF_ENDPOINT="https://YOUR_INSTANCE.jfrog.io/artifactory/api/huggingfaceml/hf-remote-proxy"
export HF_TOKEN="your-jfrog-identity-token"
export HF_HUB_DOWNLOAD_TIMEOUT=86400
export HF_HUB_ETAG_TIMEOUT=86400
```

## Policy Enforcement

| Enforcement Point | Applies To | Purpose |
|-------------------|------------|---------|
| **Curation by Label** | Remote Repository | Prevents unvetted/malicious models from being cached from public hub |
| **Xray Download Block** | Local Repository | Blocks use of models with known CVEs even if already cached |
