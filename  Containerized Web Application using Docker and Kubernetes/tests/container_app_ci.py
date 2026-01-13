import importlib.util
import os

spec = importlib.util.spec_from_file_location("container_app",
    os.path.join(os.path.dirname(__file__), '..', 'app.py'))
container_app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(container_app)


def test_root_smoke():
    app = getattr(container_app, 'app', None)
    assert app is not None
