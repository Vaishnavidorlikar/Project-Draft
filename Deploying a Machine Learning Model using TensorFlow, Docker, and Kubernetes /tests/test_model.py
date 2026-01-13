import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import importlib


def test_import_model_module():
    mod = importlib.import_module('python')
    assert mod is not None
