import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
from app_gcp import lambda_handler

def test_gcp_handler():
    event = {"name": "World"}
    resp = lambda_handler(event)
    assert isinstance(resp, tuple) and resp[1] == 200
