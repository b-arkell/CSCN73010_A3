"""Shared pytest fixtures."""
import pytest

from app import app as flask_app


@pytest.fixture(name="client")
def client_fixture():
    """Provide a Flask test client for sending fake requests to the app."""
    flask_app.config["TESTING"] = True
    # Route tests post forms directly, so skip CSRF here;
    # test_csrf_token_required turns it back on to test it.
    flask_app.config["WTF_CSRF_ENABLED"] = False
    with flask_app.test_client() as test_client:
        yield test_client
