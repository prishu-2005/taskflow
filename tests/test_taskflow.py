import sys
from pathlib import Path

# Allow Python to find the backend modules.
BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from schemas import TaskCreate, QuickAddRequest
from pydantic import ValidationError


def test_valid_task():
    task = TaskCreate(
        title="Complete resume",
        priority="high",
        project_id=1
    )

    assert task.title == "Complete resume"
    assert task.priority == "high"
    assert task.project_id == 1


def test_task_title_is_trimmed():
    task = TaskCreate(
        title="  Learn Python  ",
        priority="medium",
        project_id=1
    )

    assert task.title == "Learn Python"


def test_blank_task_title_is_rejected():
    try:
        TaskCreate(
            title="   ",
            priority="high",
            project_id=1
        )
        assert False, "Blank task titles should be rejected"
    except ValidationError:
        assert True


def test_invalid_priority_is_rejected():
    try:
        TaskCreate(
            title="Complete project",
            priority="urgent",
            project_id=1
        )
        assert False, "Invalid priorities should be rejected"
    except ValidationError:
        assert True


def test_valid_quick_add_request():
    request = QuickAddRequest(
        description="Finish resume tomorrow",
        project_id=1
    )

    assert request.description == "Finish resume tomorrow"
    assert request.project_id == 1


def test_blank_quick_add_description_is_rejected():
    try:
        QuickAddRequest(
            description="   ",
            project_id=1
        )
        assert False, "Blank descriptions should be rejected"
    except ValidationError:
        assert True


def test_create_project(client):
    response = client.post(
        "/users",
        json={
            "name": "Test User",
            "email": "testuser@example.com",
        },
    )
    assert response.status_code in (200, 201)
    user_id = response.json()["id"]

    response = client.post(
        "/projects",
        json={
            "name": "Test Project",
            "owner_id": user_id,
        },
    )

    assert response.status_code in (200, 201)
    assert response.json()["name"] == "Test Project"


def test_create_task(client):
    user_response = client.post(
        "/users",
        json={
            "name": "Task Tester",
            "email": "tasktester@example.com",
        },
    )
    user_id = user_response.json()["id"]

    project_response = client.post(
        "/projects",
        json={
            "name": "Task Test Project",
            "owner_id": user_id,
        },
    )
    project_id = project_response.json()["id"]

    response = client.post(
        "/tasks",
        json={
            "title": "Test automated task",
            "priority": "high",
            "status": "todo",
            "project_id": project_id,
        },
    )

    assert response.status_code in (200, 201)
    assert response.json()["title"] == "Test automated task"
    assert response.json()["priority"] == "high"


def test_quick_add_task(client):
    user_response = client.post(
        "/users",
        json={
            "name": "Quick Add Tester",
            "email": "quickadd@example.com",
        },
    )
    user_id = user_response.json()["id"]

    project_response = client.post(
        "/projects",
        json={
            "name": "Quick Add Project",
            "owner_id": user_id,
        },
    )
    project_id = project_response.json()["id"]

    response = client.post(
        "/tasks/quick-add",
        json={
            "description": "Finish resume urgently",
            "project_id": project_id,
        },
    )

    assert response.status_code in (200, 201)
    assert response.json()["priority"] == "high"
    assert "resume" in response.json()["title"].lower()


def test_quick_add_rejects_blank_description(client):
    response = client.post(
        "/tasks/quick-add",
        json={
            "description": "   ",
            "project_id": 1,
        },
    )

    assert response.status_code == 422
