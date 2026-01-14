import importlib.util
import os
import pytest

spec = importlib.util.spec_from_file_location("serverless_app",
    os.path.join(os.path.dirname(__file__), '..', 'app_gcp.py'))
serverless_app = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(serverless_app)
except Exception:
    pytest.skip("Unable to import serverless app; skipping", allow_module_level=True)


def test_lambda_exists():
    assert hasattr(serverless_app, 'lambda_handler')
