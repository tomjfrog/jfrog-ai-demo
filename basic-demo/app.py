"""
Standalone inference server for local/Docker deployment.

Use this when running the container outside JFrog ML (e.g. pushed to Artifactory).
For JFrog ML deployment, use: frogml models build
"""

import os
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

# Set HuggingFace endpoint to Artifactory before importing model
# HF_ENDPOINT and HF_TOKEN should be set via environment
if os.getenv("HF_ENDPOINT"):
    os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "86400")
    os.environ.setdefault("HF_HUB_ETAG_TIMEOUT", "86400")

from main.model import SentimentClassifier

app = FastAPI(
    title="JFrog AI Demo - Sentiment Classifier",
    description="HuggingFace model from Artifactory, containerized with FrogML SDK",
    version="1.0.0",
)

# Load model at startup
model = SentimentClassifier()
model.build()


class PredictRequest(BaseModel):
    """Request body for prediction."""

    text: str | list[str]


class PredictResponse(BaseModel):
    """Response with predictions."""

    predictions: list[dict]


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    """
    Run sentiment classification on input text(s).
    """
    import pandas as pd

    texts = [request.text] if isinstance(request.text, str) else request.text
    df = pd.DataFrame({"text": texts})
    result = model.predict(df)
    return PredictResponse(predictions=result.to_dict(orient="records"))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
