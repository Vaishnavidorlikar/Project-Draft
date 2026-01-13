import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from app import app

@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client

def test_root(client):
    rv = client.get('/')
    assert rv.status_code == 200
    data = rv.get_json()
    assert data.get('message') == 'Hello, World!'
