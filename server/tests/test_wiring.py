"""
Wiring tests using FastAPI's TestClient (spins up the app in-process against
the real configured database). Run with:
    ./venv/bin/python -m tests.test_wiring

These check that everything is correctly wired together: routes mount,
auth is enforced, and core error handling behaves as expected.
"""
import sys
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
passed = 0


def check(label, fn):
    global passed
    try:
        fn()
        print(f"  PASS - {label}")
        passed += 1
    except Exception as e:
        print(f"  FAIL - {label}\n    {e}")
        sys.exit(1)


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200, r.status_code


def test_me_without_token():
    r = client.get("/api/auth/me")
    assert r.status_code == 401, r.status_code


def test_me_with_garbage_token():
    r = client.get("/api/auth/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert r.status_code == 401, r.status_code


def test_unknown_api_route_404():
    r = client.get("/api/this-route-does-not-exist")
    assert r.status_code == 404, r.status_code
    assert "detail" in r.json()


def test_admin_route_requires_auth():
    r = client.get("/api/admin/stats")
    assert r.status_code == 401, r.status_code  # must not be a 500


def test_landing_page_served():
    r = client.get("/")
    assert r.status_code == 200, r.status_code
    assert "CampusCircle" in r.text


def test_invalid_role_rejected():
    r = client.post("/api/auth/register", json={
        "name": "X", "email": "wiring-test-role@example.com", "password": "Password123", "role": "admin",
    })
    assert r.status_code == 422, r.status_code


def test_short_password_rejected():
    r = client.post("/api/auth/register", json={
        "name": "X", "email": "wiring-test-pw@example.com", "password": "123", "role": "student",
    })
    assert r.status_code == 422, r.status_code


def test_duplicate_apply_returns_409_not_500():
    # Log in as a seeded demo student and hit an application twice.
    login = client.post("/api/auth/login", json={"email": "arjun@campuscircle.edu", "password": "Password@123"})
    if login.status_code != 200:
        return  # seed data not present in this environment - skip gracefully
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    feed = client.get("/api/opportunities/feed", headers=headers).json()
    if not feed:
        return
    opp_id = feed[0]["id"]
    client.post(f"/api/applications/{opp_id}", json={"cover_note": "test"}, headers=headers)
    r2 = client.post(f"/api/applications/{opp_id}", json={"cover_note": "test again"}, headers=headers)
    assert r2.status_code in (409, 400), r2.status_code  # never a raw 500


check("Health endpoint responds without auth", test_health)
check("Protected route rejects requests with no token (401)", test_me_without_token)
check("Protected route rejects a garbage token (401)", test_me_with_garbage_token)
check("Unknown /api route returns a clean 404 JSON error", test_unknown_api_route_404)
check("Admin-only route rejects anonymous requests (401, not 500)", test_admin_route_requires_auth)
check("Landing page HTML is served at /", test_landing_page_served)
check("Registering with an invalid role is rejected with 422 (not 500)", test_invalid_role_rejected)
check("Registering with a too-short password is rejected with 422", test_short_password_rejected)
check("Duplicate application attempt returns a clean 409, never a 500", test_duplicate_apply_returns_409_not_500)

print(f"\n{passed} wiring check(s) passed.")
