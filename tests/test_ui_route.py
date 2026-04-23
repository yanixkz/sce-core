from fastapi.testclient import TestClient

from sce.api import build_app


def test_ui_route_exists_and_returns_html():
    client = TestClient(build_app())
    resp = client.get('/ui')

    assert resp.status_code == 200
    assert 'text/html' in resp.headers['content-type']


def test_ui_contains_key_product_markers():
    client = TestClient(build_app())
    body = client.get('/ui').text

    assert 'SCE Core — Minimal Product Surface' in body
    assert 'Run supplier-risk demo' in body
    assert 'Run hypothesis demo' in body
    assert 'Graph inspection' in body
