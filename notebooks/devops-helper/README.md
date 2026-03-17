# DevOps Helper – LLM Fine-Tuning Notebook

**Goal: Fine-tune a Qwen 1.5 model on DevOps instructions and log it to Artifactory.** This demo uses LoRA (Parameter-Efficient Fine-Tuning) to adapt `Qwen/Qwen1.5-0.5B-Chat` on the `Szaid3680/Devops` dataset, then uploads the fine-tuned model to JFrog Artifactory for deployment.

## Workflow and Artifactory Integration

This notebook follows a single workflow where **Artifactory is the central control point** for everything:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  Local Training                                                          Artifactory │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                   │
│  1. Dependencies  ─────────────►  Conda via .condarc  ─────────────►  Packages   │
│     (PyTorch, transformers, etc.)     (fetches from Artifactory)    (cached)     │
│                                                                                   │
│  2. Base Model   ─────────────►  HF_ENDPOINT + HF_TOKEN  ──────────►  HuggingFace │
│     (Qwen/Qwen1.5-0.5B-Chat)    (Artifactory proxy)                  remote      │
│                                                                                   │
│  3. Fine-tuned   ─────────────►  frogml.huggingface.log_model  ───►  Model       │
│     Model + Artifacts           (JF_MODEL_REPO)                    registry     │
│                                                                                   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

**What this means in practice:**

- **Dependencies** – Conda and pip packages come from Artifactory (via `.condarc`), not from public channels. You control versions, scans, and governance.
- **Model download** – The base model is loaded through Artifactory’s HuggingFace proxy (when `HF_ENDPOINT` is set). Traffic goes through Artifactory, which can cache and audit models.
- **Model upload** – The fine-tuned model, tokenizer, and metadata are uploaded to JFrog via `frogml.huggingface.log_model`. Each run creates a new version (e.g. `0.0.1-20250309-143052`). The logged model can then be built and deployed as a real-time or batch API in JFrogML.

## What the Notebook Does

1. **Configuration** – Loads `HF_ENDPOINT` and `HF_TOKEN` from `devops-helper/.env` for the Artifactory HuggingFace proxy. `HF_ENDPOINT` must be set *before* any Hugging Face library is imported (it is read at import time), so the Imports cell loads `.env` first.
2. **Data** – Loads `Szaid3680/Devops`, formats for instruction tuning.
3. **Model** – Downloads base model via Artifactory (when `HF_ENDPOINT` is set), applies LoRA, trains with SFTTrainer.
4. **Evaluation** – Compares fine-tuned vs base model on a sample DevOps prompt.
5. **Log to Artifactory** – Uploads via `frogml.huggingface.log_model` with a timestamped version.
6. **Next steps** – The logged model can be built and deployed as a real-time or batch API in JFrogML.

## Dependencies from Artifactory

Conda packages (PyTorch, etc.) and pip packages (transformers, peft, trl, frogml) are installed from Artifactory when `.condarc` is configured.

Place the Artifactory-generated `.condarc` in this directory. With `.condarc` configured, Conda fetches packages from **Artifactory**. `.condarc` is in `.gitignore` (it may contain credentials).

## Setup

### Conda (recommended)

```bash
conda env create -f conda.yml
conda activate devops-helper
jupyter notebook
```

### pip

```bash
pip install -r requirements.txt
jupyter notebook
```

## Running as a Python script

You can run the full workflow without Jupyter:

```bash
cd notebooks/devops-helper
conda activate devops-helper
python run_finetuning.py
```

The script loads `.env` from the same directory and runs the same steps as the notebook: dataset load, fine-tuning, evaluation, and model logging to Artifactory.

## Credentials and Repositories

Copy `notebooks/.env.example` to `devops-helper/.env` and set:

| Variable | Purpose |
|----------|---------|
| `HF_ENDPOINT` | Artifactory HuggingFace remote URL for model download (e.g. `https://YOUR_INSTANCE.jfrog.io/artifactory/api/huggingfaceml/hf-remote`) |
| `HF_TOKEN` | Artifactory access token for HuggingFace proxy |
| `JF_MODEL_REPO` | (Optional) JFrog repository for uploading the fine-tuned model. Default: `devops-helper-llms` |

**Inputs you need:**

- **Model source**: A HuggingFace remote in Artifactory (e.g. `hf-remote`) that proxies HuggingFace. Set `HF_ENDPOINT` to its API URL.
- **Model upload**: A JFrog ML repository for the fine-tuned model (e.g. `devops-helper-llms` or `llms`). Create it in Artifactory if needed. Override via `JF_MODEL_REPO`.
