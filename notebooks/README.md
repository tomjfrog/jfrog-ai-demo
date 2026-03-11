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
└── fraud-detection/          # CatBoost / XGBoost fraud model
    ├── conda.yml             # Conda environment (recommended)
    ├── requirements.txt      # pip fallback for CI / non-Conda users
    ├── credit-card-fraud-detection.ipynb
    ├── main/
    │   ├── model.py
    │   ├── data_processor.py
    │   └── small_fraud_dataset.csv
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

**Or with pip:**

```bash
pip install -r notebooks/fraud-detection/requirements.txt
cd notebooks/fraud-detection
jupyter notebook
```

## Credentials

Copy `.env.example` to `.env` in `notebooks/` and fill in:

- `JF_URL`, `JF_ACCESS_TOKEN` – FrogML / Artifactory
- `HF_ENDPOINT`, `HF_TOKEN` – HuggingFace proxy (sentiment demos)

## CI

The `notebooks-execute.yml` workflow runs all notebooks in `sentiment/` and `fraud-detection/` to verify they execute. Fraud detection uses `requirements.txt` (pip) in CI; Conda is for local use.
