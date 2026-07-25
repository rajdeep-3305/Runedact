from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"]


def test_list_problems():
    response = client.get("/api/v1/problems")
    assert response.status_code == 200
    problems = response.json()
    assert len(problems) >= 3
    ids = [p["id"] for p in problems]
    assert "two-sum" in ids
    assert "valid-parentheses" in ids


def test_run_code_accepted():
    code = """
def two_sum(nums: list[int], target: int) -> list[int]:
    seen = {}
    for i, n in enumerate(nums):
        diff = target - n
        if diff in seen:
            return [seen[diff], i]
        seen[n] = i
    return []
"""
    response = client.post("/api/v1/run", json={"problem_id": "two-sum", "code": code})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "accepted"
    assert data["passed_count"] == data["total_count"]


def test_analyze_ast():
    code = """
def two_sum(nums, target):
    for i in range(len(nums)):
        for j in range(len(nums)):
            pass
"""
    response = client.post("/api/v1/analyze", json={"code": code})
    assert response.status_code == 200
    data = response.json()
    assert data["max_loop_depth"] == 2
    assert any("Nested loop" in ap and "O(N²)" in ap for ap in data["anti_patterns"])
    assert "O(N²)" in data["estimated_complexity"]


def test_mentor_hint():
    code = "def two_sum(nums, target): pass"
    response = client.post(
        "/api/v1/mentor/hint",
        json={"problem_id": "two-sum", "code": code, "hint_level": 1},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["hint_level"] == 1
    assert len(data["content"]) > 10
    assert data["leaked_solution"] is False
