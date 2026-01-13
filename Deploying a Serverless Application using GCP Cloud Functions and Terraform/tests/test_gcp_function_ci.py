import importlib.util
import os
import pytest

spec = importlib.util.spec_from_file_location("app_gcp",
    os.path.join(os.path.dirname(__file__), '..', 'app_gcp.py'))
app_gcp = importlib.util.module_from_spec(spec)

try:
    spec.loader.exec_module(app_gcp)
except ModuleNotFoundError:
    pytest.skip("Google Cloud libraries not installed in runner; skipping Cloud Function import test", allow_module_level=True)


def test_gcp_handler_exists():
    assert hasattr(app_gcp, 'lambda_handler')
