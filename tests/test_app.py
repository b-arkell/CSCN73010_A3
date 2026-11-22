"""Tests for the Flask routes in app.py."""
import io
from unittest.mock import patch

from PIL import Image

ERROR_MSG = b"File cannot be processed."


def _make_png(mode="RGB", size=(64, 64)):
    """Create a small in-memory PNG image for uploading."""
    buf = io.BytesIO()
    Image.new(mode, size).save(buf, format="PNG")
    buf.seek(0)
    return buf


def test_home_page_loads(client):
    """Normal case: GET / returns the HTML upload page."""
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.mimetype == "text/html"


def test_valid_upload_returns_prediction(client):
    """Normal case: a valid image produces a prediction (model is mocked)."""
    with patch("app.predict_result", return_value=7) as mock_predict:
        data = {"file": (_make_png(), "digit.png")}
        resp = client.post("/prediction", data=data, content_type="multipart/form-data")
    assert resp.status_code == 200
    mock_predict.assert_called_once()
    assert ERROR_MSG not in resp.data
    assert b"7" in resp.data


def test_missing_file_shows_error(client):
    """Edge case: submitting the form with no file shows the error message."""
    resp = client.post("/prediction", data={}, content_type="multipart/form-data")
    assert resp.status_code == 200
    assert ERROR_MSG in resp.data


def test_non_image_file_shows_error(client):
    """Edge case: a text file instead of an image is rejected gracefully."""
    data = {"file": (io.BytesIO(b"this is not an image"), "notes.txt")}
    resp = client.post("/prediction", data=data, content_type="multipart/form-data")
    assert ERROR_MSG in resp.data


def test_empty_file_shows_error(client):
    """Edge case: a zero-byte upload is rejected gracefully."""
    data = {"file": (io.BytesIO(b""), "empty.png")}
    resp = client.post("/prediction", data=data, content_type="multipart/form-data")
    assert ERROR_MSG in resp.data


def test_get_on_prediction_not_allowed(client):
    """Edge case: /prediction only accepts POST, so GET returns 405."""
    resp = client.get("/prediction")
    assert resp.status_code == 405

def test_oversized_upload_rejected(client):
    """Edge case: an upload over the 5 MB limit is rejected with 413."""
    big_file = io.BytesIO(b"0" * (6 * 1024 * 1024))
    data = {"file": (big_file, "huge.png")}
    resp = client.post("/prediction", data=data, content_type="multipart/form-data")
    assert resp.status_code == 413
    assert b"File is too large" in resp.data

def test_csrf_token_required(client):
    """Security case: a POST without a CSRF token is blocked with 400."""
    client.application.config["WTF_CSRF_ENABLED"] = True
    try:
        data = {"file": (_make_png(), "digit.png")}
        resp = client.post("/prediction", data=data, content_type="multipart/form-data")
    finally:
        client.application.config["WTF_CSRF_ENABLED"] = False
    assert resp.status_code == 400
    assert b"CSRF token" in resp.data


def test_home_page_includes_csrf_token(client):
    """Normal case: the upload form contains a hidden CSRF token field."""
    resp = client.get("/")
    assert b'name="csrf_token"' in resp.data
