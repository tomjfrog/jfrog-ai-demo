"""
Sentiment classification model using HuggingFace transformers.

Loads a pre-trained model from an Artifactory HuggingFace repository.
Configure via environment variables:
  - HF_ENDPOINT: Artifactory HuggingFace repo URL (e.g. https://<instance>.jfrog.io/artifactory/api/huggingfaceml/<repo>)
  - HF_TOKEN: Artifactory access token for authentication
  - HF_MODEL_ID: Model name (default: distilbert-base-uncased-finetuned-sst-2-english)
"""

import os

import frogml
import pandas as pd
import torch
from frogml import FrogMlModel
from frogml.sdk.model.schema import ExplicitFeature, InferenceOutput, ModelSchema


def _get_model_id() -> str:
    """Get model ID from env or use default lightweight sentiment model."""
    return os.getenv(
        "HF_MODEL_ID",
        "distilbert-base-uncased-finetuned-sst-2-english",
    )


class SentimentClassifier(FrogMlModel):
    """
    FrogML sentiment classifier using a HuggingFace model from Artifactory.

    The model is loaded from the Artifactory HuggingFace repository configured
    via HF_ENDPOINT and HF_TOKEN. If not set, falls back to public HuggingFace Hub.
    """

    def __init__(self) -> None:
        self.model_id = _get_model_id()
        self.tokenizer = None
        self.model = None

    def build(self) -> None:
        """
        Load pre-trained model from Artifactory (or HuggingFace Hub).

        HF_ENDPOINT and HF_TOKEN must be set to pull from Artifactory.
        The Artifactory repo should be a remote caching HuggingFace models.
        """
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        # When HF_ENDPOINT points to Artifactory, from_pretrained uses it
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_id)

    def schema(self) -> ModelSchema:
        """Define input/output schema for the model."""
        return ModelSchema(
            inputs=[
                ExplicitFeature(name="text", type=str),
            ],
            outputs=[
                InferenceOutput(name="label", type=str),
                InferenceOutput(name="score", type=float),
            ],
        )

    @frogml.api()
    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Run sentiment classification on input text.

        Args:
            df: DataFrame with 'text' column

        Returns:
            DataFrame with 'label' and 'score' columns
        """
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("Model not loaded. Call build() first.")

        input_texts = df["text"].astype(str).tolist()
        inputs = self.tokenizer(
            input_texts,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt",
        )

        self.model.eval()
        with torch.no_grad():
            outputs = self.model(**inputs)

        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
        scores, indices = torch.max(probs, dim=-1)

        id2label = self.model.config.id2label
        results = []
        for idx, score in zip(indices.tolist(), scores.tolist()):
            results.append(
                {
                    "label": id2label.get(idx, "unknown"),
                    "score": float(score),
                }
            )

        return pd.DataFrame(results)
