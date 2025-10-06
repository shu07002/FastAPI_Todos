import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from fastapi.testclient import TestClient
from main import app, save_todos, load_todos, TodoItem

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_and_teardown():
    # 테스트 전후로 todo 파일 초기화
    save_todos([])
    yield
    save_todos([])

def test_get_todos_empty():
    response = client.get("/todos")
    assert response.status_code == 200
    assert response.json() == []

def test_get_todos_with_items():
    todo = TodoItem(id=1, title="Test", description="Desc", completed=False)
    save_todos([todo.model_dump()])
    response = client.get("/todos")
    assert response.status_code == 200
    todos = response.json()
    assert len(todos) == 1
    assert todos[0]["title"] == "Test"

def test_create_todo():
    # id는 자동 생성되므로 보내지 않음
    todo = {"title": "Test", "description": "Desc", "completed": False}
    response = client.post("/todos", json=todo)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test"
    assert "id" in data
    assert data["priority"] == "medium"

def test_create_todo_invalid():
    # description 누락 → 유효성 검사 실패 (422)
    todo = {"title": "Test"}
    response = client.post("/todos", json=todo)
    assert response.status_code == 422

def test_update_todo():
    todo = TodoItem(id=1, title="Old", description="Old desc", completed=False)
    save_todos([todo.model_dump()])

    updated_todo = {
        "id": 1,
        "title": "Updated",
        "description": "Updated desc",
        "completed": True,
        "priority": "high",
    }
    response = client.put("/todos/1", json=updated_todo)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated"
    assert data["completed"] is True
    assert data["priority"] == "high"

def test_update_todo_not_found():
    updated_todo = {
        "id": 1,
        "title": "Updated",
        "description": "Updated desc",
        "completed": True,
    }
    response = client.put("/todos/1", json=updated_todo)
    assert response.status_code == 404
    assert response.json()["detail"] == "To-Do item not found"

def test_delete_todo():
    todo = TodoItem(id=1, title="Del", description="To delete", completed=False)
    save_todos([todo.model_dump()])

    response = client.delete("/todos/1")
    assert response.status_code == 200
    assert response.json()["message"] == "To-Do item deleted"

    # 삭제 후 실제로 비어 있는지 확인
    todos = load_todos()
    assert len(todos) == 0

def test_delete_todo_not_found():
    response = client.delete("/todos/1")
    assert response.status_code == 404
    assert response.json()["detail"] == "To-Do item not found"
