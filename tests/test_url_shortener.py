<<<<<<< HEAD
import sqlite3
import threading

import pytest
from fastapi.testclient import TestClient

from app.main import app, store
from app.service import URLService
from app.store import SQLiteStore


@pytest.fixture
def client(tmp_path):
    original = store.path
    store.path = str(tmp_path / "urls.db")
    store.initialize()
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    store.path = original


def test_shorten_redirect_and_analytics(client):
    response = client.post("/api/shorten", json={"url": "https://example.com/path"})
    assert response.status_code == 201
    code = response.json()["code"]
=======
import tempfile

from fastapi.testclient import TestClient

from app.main import app, store

client = TestClient(app)
store.path = tempfile.mktemp(suffix=".db")
store.initialize()


def test_shorten_redirect_and_analytics():
    response = client.post("/api/shorten", json={"url": "https://example.com/path"})
    assert response.status_code == 201
    body = response.json()
    code = body["code"]
>>>>>>> origin/main
    redirect = client.get(f"/{code}", follow_redirects=False)
    assert redirect.status_code == 302
    assert redirect.headers["location"] == "https://example.com/path"
    analytics = client.get(f"/api/urls/{code}/analytics")
    assert analytics.status_code == 200
    assert analytics.json()["clicks"] == 1


<<<<<<< HEAD
def test_custom_code_conflict(client):
    first = client.post(
        "/api/shorten", json={"url": "https://example.com", "custom_code": "test-code"}
    )
    assert first.status_code == 201
    second = client.post(
        "/api/shorten", json={"url": "https://another.example", "custom_code": "test-code"}
=======
def test_custom_code_conflict():
    code = "test-code"
    first = client.post("/api/shorten", json={"url": "https://example.com", "custom_code": code})
    assert first.status_code == 201
    second = client.post(
        "/api/shorten", json={"url": "https://another.example", "custom_code": code}
>>>>>>> origin/main
    )
    assert second.status_code == 409


<<<<<<< HEAD
def test_unknown_code_is_404(client):
=======
def test_unknown_code_is_404():
>>>>>>> origin/main
    assert client.get("/does-not-exist").status_code == 404
    assert client.get("/api/urls/no-such-code/analytics").status_code == 404


<<<<<<< HEAD
@pytest.mark.parametrize(
    "url",
    [
        "http://localhost:8080/admin",
        "http://LOCALHOST./admin",
        "http://127.0.0.1/",
        "http://0.0.0.0/",
        "http://10.0.0.5/admin",
        "http://172.16.0.1/",
        "http://192.168.1.1/",
        "http://100.64.0.1/",
        "http://169.254.169.254/latest/meta-data",
        "http://[::1]/",
        "http://[::ffff:127.0.0.1]/",
        "http://[fd00::1]/",
        "http://printer.local/",
        "http://svc.internal/",
        "ftp://example.com/file",
    ],
)
def test_reject_non_public_destinations(client, url):
    assert client.post("/api/shorten", json={"url": url}).status_code == 422


@pytest.mark.parametrize("url", ["https://example.com", "http://93.184.216.34/page"])
def test_accept_public_destinations(client, url):
    assert client.post("/api/shorten", json={"url": url}).status_code == 201


@pytest.mark.parametrize("code", ["docs", "DOCS", "health", "redoc", "api"])
def test_reserved_custom_codes_rejected(client, code):
    # 'api' is shorter than the 4-character minimum, so it fails on length; the rest on the
    # reserved-word rule. Either way it must never be stored.
    response = client.post("/api/shorten", json={"url": "https://example.com", "custom_code": code})
    assert response.status_code == 422
    assert client.get("/health").json() == {"status": "ok"}


def test_concurrent_custom_code_claims_yield_one_winner(tmp_path):
    """Regression: check-then-insert raced and surfaced IntegrityError as HTTP 500."""
    service = URLService(SQLiteStore(str(tmp_path / "race.db")))
    service.store.initialize()
    results, barrier = [], threading.Barrier(8)

    def claim():
        barrier.wait()
        try:
            service.shorten("https://example.com", "contested")
            results.append("ok")
        except Exception as exc:  # noqa: BLE001
            results.append(type(exc).__name__)

    threads = [threading.Thread(target=claim) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert results.count("ok") == 1
    assert set(results) == {"ok", "CodeConflict"}


def test_generated_code_collision_retries_then_503(client, monkeypatch):
    from app import main

    monkeypatch.setattr(main.service, "_new_code", lambda length=7: "fixedcode")
    assert client.post("/api/shorten", json={"url": "https://example.com"}).status_code == 201
    # Every subsequent attempt collides; the bounded loop must give up cleanly.
    assert client.post("/api/shorten", json={"url": "https://example.com"}).status_code == 503


def test_duplicate_insert_is_mapped_not_leaked(tmp_path):
    s = SQLiteStore(str(tmp_path / "dup.db"))
    s.initialize()
    s.insert_url("abcd", "https://example.com", "2026-01-01T00:00:00+00:00")
    with pytest.raises(Exception) as info:
        s.insert_url("abcd", "https://example.com", "2026-01-01T00:00:00+00:00")
    assert not isinstance(info.value, sqlite3.IntegrityError)


def test_redirect_survives_analytics_write_failure(client, monkeypatch):
    """Regression: a locked database on the click write returned 500 instead of redirecting."""
    code = client.post("/api/shorten", json={"url": "https://example.com/x"}).json()["code"]

    def locked(*_args):
        raise sqlite3.OperationalError("database is locked")

    monkeypatch.setattr(store, "record_click", locked)
    response = client.get(f"/{code}", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "https://example.com/x"
=======
def test_reject_local_destination():
    response = client.post("/api/shorten", json={"url": "http://localhost:8080/admin"})
    assert response.status_code == 422
>>>>>>> origin/main
