from fastapi.testclient import TestClient
import pytest

from src.app import app

client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_duplicate_capacity_and_unregister():
    activity = "TestActivity-Unit"
    email1 = "tester@example.com"
    email2 = "second@example.com"

    # Create a temporary activity for isolated testing
    from src import app as app_module

    app_module.activities[activity] = {
        "description": "Temporary activity for unit tests",
        "schedule": "UnitTestTime",
        "max_participants": 2,
        "participants": [],
    }

    try:
        # First signup should succeed
        r1 = client.post(f"/activities/{activity}/signup", params={"email": email1})
        assert r1.status_code == 200

        # Duplicate signup (different case/spacing) should be rejected
        r_dup = client.post(f"/activities/{activity}/signup", params={"email": "  TESTER@EXAMPLE.COM  "})
        assert r_dup.status_code == 400
        assert r_dup.json().get("detail") == "Student is already signed up for this activity"

        # Sign up a second student to reach capacity
        r2 = client.post(f"/activities/{activity}/signup", params={"email": email2})
        assert r2.status_code == 200

        # Next signup should be rejected as full
        r_full = client.post(f"/activities/{activity}/signup", params={"email": "overflow@example.com"})
        assert r_full.status_code == 400
        assert r_full.json().get("detail") == "Activity is full"

        # Unregister the first student
        rd = client.delete(f"/activities/{activity}/signup", params={"email": email1})
        assert rd.status_code == 200

        # Unregister again returns 404
        rd2 = client.delete(f"/activities/{activity}/signup", params={"email": email1})
        assert rd2.status_code == 404
        assert rd2.json().get("detail") == "Student not found in participants"

    finally:
        # Cleanup the temporary activity
        app_module.activities.pop(activity, None)
