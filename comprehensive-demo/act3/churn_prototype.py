"""
Act 3: Governed Customer Churn Prediction - Trusted AI

This implementation operationalizes AISecOps:
- JFrog Identity Token (no hardcoded secrets)
- JFrog AI Gateway for external API calls (centralized, audited)
- frogml-inference for versioned model serving (managed Data Plane)
- Models sourced via Artifactory proxy (scanned, curated)
"""

import json
import os
import sys


def get_sentiment_via_ai_gateway(text: str) -> str:
    """
    Use JFrog AI Gateway for sentiment - abstracted credentials, centralized audit.
    base_url points to the platform's AI Gateway endpoint.
    """
    from openai import OpenAI

    token = os.environ.get("JF_ACCESS_TOKEN")
    if not token:
        return "error:JF_ACCESS_TOKEN not set"

    jfrog_url = os.environ.get("JF_URL", "https://YOUR_INSTANCE.jfrog.io").rstrip("/")
    base_url = f"{jfrog_url}/artifactory/api/ai/api/v1"

    client = OpenAI(api_key=token, base_url=base_url)
    # Use approved model naming from AI Catalog (e.g., OpenAI/gpt-3.5-turbo)
    model_name = os.environ.get("AI_CATALOG_MODEL", "OpenAI/gpt-3.5-turbo")

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "Classify sentiment as positive, negative, or neutral."},
            {"role": "user", "content": text},
        ],
        max_tokens=10,
    )
    return response.choices[0].message.content.strip().lower()


def predict_churn_via_frogml(feature_vector: dict) -> dict:
    """
    Use frogml-inference RealTimeClient for churn prediction.
    Model is a versioned binary served from the secure JFrog ML Data Plane.
    """
    from frogml_inference.realtime_client import RealTimeClient

    model_id = os.environ.get("CHURN_MODEL_ID", "churn-prediction-v1")
    client = RealTimeClient(model_id=model_id)
    # RealTimeClient.predict expects a list of feature dicts
    response = client.predict([feature_vector])
    return response[0] if isinstance(response, list) and response else response


def predict_churn(feature_vector: dict, use_frogml: bool = True) -> dict:
    """
    Governed prediction: uses RealTimeClient when available, else fallback logic.
    No pickle loading - eliminates serialization attack surface.
    """
    if use_frogml:
        try:
            return predict_churn_via_frogml(feature_vector)
        except Exception as e:
            return {"error": str(e), "fallback": "frogml_unavailable"}

    # Fallback: local model from Artifactory proxy (HF_ENDPOINT/HF_TOKEN)
    sentiment_raw = feature_vector.get("review_sentiment", "neutral")
    if isinstance(sentiment_raw, str) and len(sentiment_raw) > 20:
        sentiment = get_sentiment_via_ai_gateway(sentiment_raw)
    else:
        sentiment = str(sentiment_raw).lower()

    tenure = feature_vector.get("tenure_months", 12)
    support_tickets = feature_vector.get("support_tickets", 0)

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
        "model_source": "governed_ai_gateway",
    }


def main():
    """Entry point for containerized deployment."""
    if len(sys.argv) > 1:
        data = json.loads(sys.argv[1])
    else:
        data = {
            "tenure_months": 8,
            "support_tickets": 3,
            "review_sentiment": "The product is okay but support was slow.",
        }

    use_frogml = os.environ.get("USE_FROGML_INFERENCE", "true").lower() == "true"
    result = predict_churn(data, use_frogml=use_frogml)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
