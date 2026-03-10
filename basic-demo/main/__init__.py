"""JFrog AI Demo - FrogML model with HuggingFace from Artifactory."""

from .model import SentimentClassifier

__all__ = ["SentimentClassifier"]


def load_model():
    """Return the model instance for FrogML build process."""
    return SentimentClassifier()
