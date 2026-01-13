import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from service1 import app as app1
from service2 import app as app2


def test_service_imports():
    assert app1 is not None
    assert app2 is not None
