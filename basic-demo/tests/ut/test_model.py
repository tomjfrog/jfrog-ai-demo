"""Unit tests for the sentiment classifier model."""

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

    # run_local returns list of dicts or DataFrame depending on output adapter
    assert result is not None
    if isinstance(result, list):
        assert len(result) == 2
        assert "label" in result[0] and "score" in result[0]
    else:
        result_df = pd.DataFrame(result) if not isinstance(result, pd.DataFrame) else result
        assert len(result_df) == 2
        assert "label" in result_df.columns and "score" in result_df.columns
