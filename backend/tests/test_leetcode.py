from fastapi.testclient import TestClient
from app.leetcode.client import html_to_text, leetcode_client
from app.main import app

client = TestClient(app)


def test_html_to_text():
    markup = "<p>Given an array <code>nums</code></p>"
    text = html_to_text(markup)
    assert "Given an array nums" in text


def _stub_catalog(monkeypatch):
    monkeypatch.setattr(
        leetcode_client, "_catalog",
        [
            {"id": "two-sum", "title": "Two Sum", "difficulty": "Easy",
             "tags": ["Array"], "paid_only": False},
        ],
    )
    monkeypatch.setattr(leetcode_client, "_catalog_fetched_at", float("inf"))


def test_catalog_endpoint(monkeypatch):
    _stub_catalog(monkeypatch)
    res = client.get("/api/v1/leetcode?limit=1")
    assert res.status_code == 200
    assert res.json()[0]["id"] == "two-sum"


def _stub_practice_question(monkeypatch):
    def fake_post(query, variables):
        return {
            "questionData": {
                "questionFrontendId": "1",
                "title": "Two Sum",
                "titleSlug": "two-sum",
                "difficulty": "Easy",
                "isPaidOnly": False,
                "content": "<p>Given an array of integers <code>nums</code>.</p><pre>Input: nums = [2,7,11,15], target = 9\nOutput: [0,1]</pre>",
                "hints": [],
                "topicTags": [{"name": "Array"}],
                "codeSnippets": [
                    {
                        "langSlug": "python3",
                        "code": "class Solution:\n    def twoSum(self, nums: List[int], target: int) -> List[int]:\n        pass",
                    }
                ],
            }
        }
    monkeypatch.setattr("app.leetcode.client._graphql_post", fake_post)
    leetcode_client.clear_cache()


def test_practice_pack(monkeypatch):
    _stub_practice_question(monkeypatch)
    pack = leetcode_client.practice("two-sum")
    assert pack["practice"]["entry_point"] == "Solution().twoSum"
    assert len(pack["practice"]["test_cases"]) == 1


def test_leetcode_run(monkeypatch):
    _stub_practice_question(monkeypatch)
    res = client.post(
        "/api/v1/leetcode/two-sum/run",
        json={
            "slug": "two-sum",
            "code": (
                "class Solution:\n"
                "    def twoSum(self, nums, target):\n"
                "        return [0, 1]\n"
            ),
        },
    )
    assert res.status_code == 200
    assert res.json()["status"] == "accepted"
