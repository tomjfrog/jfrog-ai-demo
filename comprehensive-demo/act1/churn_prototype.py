"""
Act 1: Rogue Baseline - Shadow AI Customer Churn Prototype

WARNING: This implementation represents the "Wild West" state of AI.
- Hardcoded API keys (data leakage risk)
- Direct downloads from public hubs (no security scanning)
- Unsafe pickle loading (serialization attack surface)
- Zero traceability or AI-BOM

This container represents a "Black Box" deployment with no governance.
"""

# Hardcoded secret - violates security policy, enables data leakage with zero oversight
OPENAI_API_KEY = "sk-shadow-ai-key-secret-12345"

import json
import os
from pathlib import Path


def load_sentiment_via_openai(text: str) -> str:
    """Use direct OpenAI API for sentiment - bypasses enterprise governance."""
    try:
        from openai import OpenAI

        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Classify sentiment as positive, negative, or neutral."},
                {"role": "user", "content": text},
            ],
            max_tokens=10,
        )
        return response.choices[0].message.content.strip().lower()
    except Exception as e:
        return f"error:{e}"


def load_model_from_huggingface():
    """Direct download from public Hugging Face Hub - no Artifactory proxy, no scanning."""
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    # Unvetted public source - models here are not scanned for malicious code
    model_id = "distilbert-base-uncased-finetuned-sst-2-english"
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForSequenceClassification.from_pretrained(model_id)
    return tokenizer, model


def load_pickle_weights(model_path: str):
    """
    Attempt to load .pkl file - represents unsafe serialization attack risk.
    Malicious pickle files can execute arbitrary code during deserialization.
    See: Rami Pinku blog on AI supply chain risks.
    """
    import pickle

    pkl_path = Path(model_path)
    if pkl_path.exists():
        with open(pkl_path, "rb") as f:
            return pickle.load(f)  # noqa: S301 - unsafe by design for demo
    return None


def predict_churn(feature_vector: dict, tokenizer=None, model=None) -> dict:
    """
    Dummy prediction function - processes feature vector and returns churn probability.
    In Act 1, model may be loaded from unvetted pickle or direct HuggingFace.
    """
    # Attempt pickle load (demonstrates serialization risk)
    pkl_weights = load_pickle_weights("model_weights.pkl")

    # Fallback: use HuggingFace model if no pickle
    if tokenizer is None or model is None:
        tokenizer, model = load_model_from_huggingface()

    # Dummy feature processing - in production would use actual model inference
    tenure = feature_vector.get("tenure_months", 12)
    support_tickets = feature_vector.get("support_tickets", 0)
    sentiment_raw = feature_vector.get("review_sentiment", "neutral")

    # Use OpenAI for sentiment if provided as text (shadow AI call)
    if isinstance(sentiment_raw, str) and len(sentiment_raw) > 20:
        sentiment = load_sentiment_via_openai(sentiment_raw)
    else:
        sentiment = str(sentiment_raw).lower()

    # Naive churn score heuristic
    churn_score = 0.0
    if "negative" in sentiment:
        churn_score += 0.4
    if support_tickets > 5:
        churn_score += 0.3
    if tenure < 6:
        churn_score += 0.2
    churn_score = min(1.0, churn_score)

    return {
        "churn_probability": round(churn_score, 4),
        "sentiment": sentiment,
        "pkl_loaded": pkl_weights is not None,
        "model_source": "direct_huggingface",
    }


def main():
    """Entry point for containerized deployment."""
    import sys

    if len(sys.argv) > 1:
        data = json.loads(sys.argv[1])
    else:
        data = {
            "tenure_months": 8,
            "support_tickets": 3,
            "review_sentiment": "The product is okay but support was slow.",
        }

    result = predict_churn(data)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
