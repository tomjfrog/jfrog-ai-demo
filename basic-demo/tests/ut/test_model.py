"""Unit tests for the sentiment classifier model."""

import json

# Import run_local first - required by FrogML for local/testing context
from frogml.sdk.model.tools import run_local  # noqa: F401

import pandas as pd

from main.model import SentimentClassifier


def test_model_schema():
    """Verify model schema is defined correctly."""
    model = SentimentClassifier()
    schema = model.schema()
    assert schema is not None
    proto = schema.to_proto()
    assert "text" in str(proto)
    assert "label" in str(proto)
    assert "score" in str(proto)


def test_model_build_and_predict():
    """Test build and predict with sample input using run_local."""
    import pytest

    try:
        model = SentimentClassifier()
        input_vector = pd.DataFrame({"text": ["This is great!", "I hate it."]}).to_json()
        result = run_local(model, input_vector)
    except ImportError as e:
        if "PyTorch" in str(e) or "torch" in str(e).lower():
            pytest.skip(f"PyTorch/transformers not fully available: {e}")
        raise

    # run_local returns list of dicts, DataFrame, dict with predictions key, or JSON string
    assert result is not None
    if isinstance(result, str):
        result = json.loads(result)
    if isinstance(result, list):
        assert len(result) == 2
        assert "label" in result[0] and "score" in result[0]
    elif isinstance(result, pd.DataFrame):
        assert len(result) == 2
        assert "label" in result.columns and "score" in result.columns
    elif isinstance(result, dict):
        # Handle dict format, e.g. {"predictions": [...]} or {"predictions": "[{...}]"}
        preds = result.get("predictions", result.get("output", result))
        if isinstance(preds, str):
            preds = json.loads(preds)
        if isinstance(preds, list):
            assert len(preds) == 2
            assert "label" in preds[0] and "score" in preds[0]
        elif isinstance(preds, pd.DataFrame):
            assert len(preds) == 2
            assert "label" in preds.columns and "score" in preds.columns
        elif isinstance(preds, pd.Series):
            # Series of chars from JSON string - reconstruct and parse
            preds = json.loads("".join(preds.astype(str)))
            assert len(preds) == 2
            assert "label" in preds[0] and "score" in preds[0]
        else:
            result_df = pd.DataFrame(preds)
            assert len(result_df) == 2
            assert "label" in result_df.columns and "score" in result_df.columns
    else:
        result_df = pd.DataFrame(list(result)) if hasattr(result, "__iter__") else pd.DataFrame([result])
        assert len(result_df) == 2
        assert "label" in result_df.columns and "score" in result_df.columns
