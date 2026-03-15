# JFrog AI Demo – Jupyter Notebooks

Interactive notebook scenarios for JFrog AI/ML Ops demos. Each **scenario** has its own subdirectory with environment config (Conda and/or pip).

## Directory structure

```
notebooks/
├── README.md                 # This file
├── .env.example              # Shared credentials template
├── requirements.txt          # Base deps for sentiment demos (pip)
│
├── sentiment/                # HuggingFace / transformers demos
│   ├── 01-sentiment-from-artifactory.ipynb
│   ├── 02-frogml-log-model-ai-bom.ipynb
│   └── 03-huggingface-proxy-demo.ipynb
│
├── fraud-detection/          # CatBoost / XGBoost fraud model
│   ├── conda.yml
│   ├── requirements.txt
│   ├── credit-card-fraud-detection.ipynb
│   ├── main/
│   └── README.md
│
└── devops-helper/            # Qwen LLM fine-tuning (LoRA)
    ├── conda.yml
    ├── requirements.txt
    ├── llm_finetuning_devops.ipynb
    ├── code_dir/
    │   └── predict.py
    ├── main/
    └── README.md
```

## Environment setup by scenario

### Sentiment (pip)

Uses the root `requirements.txt` (transformers, torch, frogml, jupyter).

```bash
pip install -r notebooks/requirements.txt
cd notebooks/sentiment
jupyter notebook
```

### Fraud detection (Conda recommended)

Uses CatBoost, XGBoost, scikit-learn. Conda handles native deps better.

```bash
cd notebooks/fraud-detection
conda env create -f conda.yml
conda activate fraud-detection
jupyter notebook
```

### DevOps Helper (Conda recommended)

LLM fine-tuning with transformers, peft, trl. Conda handles PyTorch and native deps.

```bash
cd notebooks/devops-helper
conda env create -f conda.yml
conda activate devops-helper
jupyter notebook
```

**Or with pip (fraud-detection / devops-helper):**

```bash
pip install -r notebooks/fraud-detection/requirements.txt
# or
pip install -r notebooks/devops-helper/requirements.txt
cd notebooks/fraud-detection  # or devops-helper
jupyter notebook
```

## Credentials

Copy `.env.example` to `.env` in `notebooks/` and fill in:

- `JF_URL`, `JF_ACCESS_TOKEN` – FrogML / Artifactory
- `HF_ENDPOINT`, `HF_TOKEN` – HuggingFace proxy (sentiment, devops-helper)
- `JF_MODEL_REPO` – (optional) Model upload repo for devops-helper

## CI

The `notebooks-execute.yml` workflow runs all notebooks in `sentiment/`, `fraud-detection/`, and `devops-helper/` to verify they execute. Fraud detection and devops-helper use `requirements.txt` (pip) in CI; Conda is for local use.
