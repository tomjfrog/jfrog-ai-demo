# Fraud Detection Notebook

**Goal: Build a model from scratch.** This demo trains a credit card fraud classifier from the ground up—no pre-trained models, no transfer learning, no fine-tuning. You train Random Forest, XGBoost, and CatBoost on local data, pick the best one, and log it to Artifactory for deployment.

## What the Notebook Does

The notebook walks through a full ML workflow from raw data to a model stored in Artifactory:

1. **Load the data** – Reads a credit card transaction dataset (`main/small_fraud_dataset.csv`) with ~3,800 rows. Each row has anonymized features (Time, V1–V28, Amount) and a Class label (0 = legitimate, 1 = fraud).

2. **Explore the data** – Inspects shape, summary stats, and class balance. Fraud is rare (about 1.3% of transactions), so the dataset is imbalanced.

3. **Preprocess** – Splits into train/test, scales numeric features with StandardScaler, and prepares data for training.

4. **Train three models** – Trains Random Forest, XGBoost, and CatBoost. Uses RandomizedSearchCV to tune hyperparameters and F1-score for evaluation (important for imbalanced fraud detection).

5. **Compare models** – Evaluates accuracy, F1, precision, and recall. Chooses the best model (typically CatBoost).

6. **Log to Artifactory** – Uploads the best model to JFrog Artifactory via `frogml.catboost.log_model`, including hyperparameters and metrics. The version uses a timestamp suffix (e.g. `0.0.1-20251217-143052`) so each run creates a new version.

7. **Next steps** – The logged model can be built and deployed as a real-time or batch API in JFrogML.

## Dependencies from Artifactory

The classifiers (Random Forest, XGBoost, CatBoost) are Python packages—algorithm implementations installed by Conda. They are not pre-trained models; they are libraries that you instantiate and train on your data.

Place the Artifactory-generated `.condarc` in this directory. With `.condarc` configured, Conda fetches these packages from **Artifactory**—the central control point for all packages, binaries, and artifacts in this demo. Instead of pulling scikit-learn, catboost, xgboost, and other dependencies directly from public channels, they flow through Artifactory: cached, scanned, and governed in one place.

This is the first peek at the advantage of using the JFrog Platform for all workflows and related dependencies. Generate `.condarc` from the Artifactory UI (Conda virtual repo → Set Me Up). `.condarc` is in `.gitignore` (it may contain credentials).

---

## Setup

### Conda (recommended)

```bash
conda env create -f conda.yml
conda activate fraud-detection
jupyter notebook
```

### pip

```bash
pip install -r requirements.txt
jupyter notebook
```

## Credentials

Set `JF_URL` and `JF_ACCESS_TOKEN` (or use `../.env`) for Artifactory model logging.
