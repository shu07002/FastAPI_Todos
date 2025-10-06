import requests

BASE_URL = "http://3.35.93.179:8002"  # 배포된 서버 주소

def test_server_health():
    """서버가 응답하는지 확인"""
    response = requests.get(f"{BASE_URL}/todos")
    assert response.status_code == 200

def test_create_todo():
    """To-Do 생성이 잘 되는지 확인"""
    data = {
        "title": "Jenkins Test",
        "description": "Created from Jenkins test stage",
        "completed": False
    }
    response = requests.post(f"{BASE_URL}/todos", json=data)
    assert response.status_code == 200
    assert response.json()["title"] == "Jenkins Test"
