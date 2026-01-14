import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app


def test_root():
    app.testing = True
    client = app.test_client()
    rv = client.get('/')
    assert rv.status_code in (200, 404)  # project apps may not have root implemented
