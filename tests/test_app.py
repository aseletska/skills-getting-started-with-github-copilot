import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_activities():
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)


def test_get_activities_returns_activity_list():
    response = client.get("/activities")

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_adds_student_to_activity():
    activity_name = "Chess Club"
    email = "new.student@mergington.edu"

    response = client.post(
        f"/activities/{quote(activity_name)}/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert email in activities[activity_name]["participants"]


def test_signup_rejects_duplicate_student():
    activity_name = "Chess Club"
    email = "duplicate.student@mergington.edu"

    first_response = client.post(
        f"/activities/{quote(activity_name)}/signup",
        params={"email": email},
    )
    second_response = client.post(
        f"/activities/{quote(activity_name)}/signup",
        params={"email": email},
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 400
    assert activities[activity_name]["participants"].count(email) == 1


def test_signup_unknown_activity_returns_404():
    response = client.post(
        "/activities/Unknown%20Activity/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404


def test_unregister_removes_student_from_activity():
    activity_name = "Chess Club"
    email = "remove.student@mergington.edu"

    activities[activity_name]["participants"].append(email)

    response = client.delete(
        f"/activities/{quote(activity_name)}/participants/{quote(email)}"
    )

    assert response.status_code == 200
    assert email not in activities[activity_name]["participants"]


def test_unregister_unknown_activity_returns_404():
    response = client.delete(
        "/activities/Unknown%20Activity/participants/student%40mergington.edu"
    )

    assert response.status_code == 404


def test_unregister_unknown_participant_returns_404():
    activity_name = "Chess Club"
    email = "missing.student@mergington.edu"

    response = client.delete(
        f"/activities/{quote(activity_name)}/participants/{quote(email)}"
    )

    assert response.status_code == 404