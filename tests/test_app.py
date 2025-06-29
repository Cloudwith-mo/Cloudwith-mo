import os
import sys
import pytest
import importlib

flask_spec = importlib.util.find_spec("flask")
pytestmark = pytest.mark.skipif(flask_spec is None, reason="Flask not installed")

# Ensure we run the app from its directory so relative paths work
@pytest.fixture(scope="module", autouse=True)
def change_dir():
    cwd = os.getcwd()
    target = os.path.join(cwd, "tax_portal")
    os.chdir(target)
    sys.path.insert(0, target)
    yield
    os.chdir(cwd)
    if target in sys.path:
        sys.path.remove(target)

def test_login_page_loads():
    from app import app
    client = app.test_client()
    response = client.get('/login')
    assert response.status_code == 200
    assert b"Login" in response.data

def test_static_css_served():
    from app import app
    client = app.test_client()
    response = client.get('/static/style.css')
    assert response.status_code == 200
    assert b"font-family" in response.data
