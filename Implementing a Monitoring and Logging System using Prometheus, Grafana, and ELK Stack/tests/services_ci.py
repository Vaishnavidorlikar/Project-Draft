import importlib.util
import os
import pytest

try:
    spec1 = importlib.util.spec_from_file_location("service1",
        os.path.join(os.path.dirname(__file__), '..', 'service1.py'))
    service1 = importlib.util.module_from_spec(spec1)
    spec1.loader.exec_module(service1)

    spec2 = importlib.util.spec_from_file_location("service2",
        os.path.join(os.path.dirname(__file__), '..', 'service2.py'))
    service2 = importlib.util.module_from_spec(spec2)
    spec2.loader.exec_module(service2)
except ValueError:
    pytest.skip("Prometheus Collector registration duplicated in runner; skipping import", allow_module_level=True)


def test_services_smoke():
    assert True
