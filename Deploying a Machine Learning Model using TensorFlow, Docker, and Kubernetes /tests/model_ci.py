import importlib.util
import os
import pytest

spec = importlib.util.spec_from_file_location("ml_model",
    os.path.join(os.path.dirname(__file__), '..', 'python.py'))
ml_model = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(ml_model)
except ModuleNotFoundError:
    pytest.skip("TensorFlow not installed in runner; skipping ML model import test", allow_module_level=True)


def test_model_importable():
    assert ml_model is not None
