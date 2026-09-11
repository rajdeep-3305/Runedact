from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_list_problems():
    response = client.get("/api/v1/problems")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_run_code():
    code = """
def two_sum(nums, target):
    seen = {}
    for i, n in enumerate(nums):
        if target - n in seen:
            return [seen[target - n], i]
        seen[n] = i
    return []
"""
    response = client.post("/api/v1/run", json={"problem_id": "two-sum", "code": code})
    assert response.status_code == 200
    assert response.json()["status"] == "accepted"


def test_analyze_ast():
    code = """
def two_sum(nums, target):
    for i in range(len(nums)):
        for j in range(len(nums)):
            pass
"""
    response = client.post("/api/v1/analyze", json={"code": code})
    assert response.status_code == 200
    assert response.json()["max_loop_depth"] == 2


def test_mentor_hint():
    code = "def two_sum(nums, target): pass"
    response = client.post(
        "/api/v1/mentor/hint",
        json={"problem_id": "two-sum", "code": code, "hint_level": 1},
    )
    assert response.status_code == 200
    assert "content" in response.json()
