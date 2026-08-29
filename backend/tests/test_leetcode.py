
from fastapi.testclient import TestClient

from app.leetcode.client import LeetCodeError, html_to_text, leetcode_client
from app.main import app


client = TestClient(app)


def test_html_to_text_preserves_pre_and_list_structure():
    markup = (
        "<p>Given an array <code>nums</code></p>"
        "<pre>nums[i] == target</pre>"
        "<ul><li>first</li><li>second</li></ul>"
    )
    text = html_to_text(markup)
    assert "Given an array nums" in text
    assert "nums[i] == target" in text
    assert "\n• first" in text
    assert "\n• second" in text


def test_html_to_text_collapses_blank_runs():
    text = html_to_text("<p>a</p><p></p><p></p><p>b</p>")
    assert "\n\n\n" not in text


def _stub_catalog(monkeypatch):
    monkeypatch.setattr(
        leetcode_client, "_catalog",
        [
            {"id": "two-sum", "title": "Two Sum", "difficulty": "Easy",
             "tags": ["Array"], "paid_only": False},
            {"id": "median-of-two-sorted-arrays", "title": "Median of Two Sorted Arrays",
             "difficulty": "Hard", "tags": ["Array"], "paid_only": True},
        ],
    )
    monkeypatch.setattr(leetcode_client, "_catalog_fetched_at", float("inf"))


def _stub_question(monkeypatch):
    def fake_question(slug: str):
        if slug == "two-sum":
            return {
                "id": "two-sum", "title": "Two Sum", "difficulty": "Easy",
                "tags": ["Array"], "paid_only": False,
                "description": "Given an array of integers...",
                "hints": ["A hash map helps."],
            }
        raise LeetCodeError(f"no leetcode problem named '{slug}'")

    monkeypatch.setattr(leetcode_client, "question", fake_question)


def test_catalog_endpoint_maps_fields(monkeypatch):
    _stub_catalog(monkeypatch)
    res = client.get("/api/v1/leetcode?limit=1")
    assert res.status_code == 200
    body = res.json()
    assert len(body) == 1
    assert body[0]["id"] == "two-sum"
    assert body[0]["paid_only"] is False


def test_question_endpoint_and_bad_slug(monkeypatch):
    _stub_question(monkeypatch)
    res = client.get("/api/v1/leetcode/two-sum")
    assert res.status_code == 200
    assert res.json()["hints"] == ["A hash map helps."]

    res = client.get("/api/v1/leetcode/not a slug!")
    assert res.status_code == 400


def test_upstream_failure_surfaces_as_503(monkeypatch):
    def boom(slug: str):
        raise LeetCodeError("could not reach leetcode")

    monkeypatch.setattr(leetcode_client, "question", boom)
    res = client.get("/api/v1/leetcode/two-sum")
    assert res.status_code == 503


def test_client_caches_question_within_ttl(monkeypatch):
    leetcode_client.clear_cache()
    calls = {"count": 0}

    def fake_post(query, variables):
        calls["count"] += 1
        return {
            "questionData": {
                "questionFrontendId": "1", "title": "Two Sum",
                "titleSlug": "two-sum", "difficulty": "Easy",
                "isPaidOnly": False, "content": "<p>hi</p>", "hints": [],
                "topicTags": [{"name": "Array"}],
            }
        }

    monkeypatch.setattr("app.leetcode.client._graphql_post", fake_post)
    leetcode_client.question("two-sum")
    leetcode_client.question("two-sum")
    assert calls["count"] == 1
    leetcode_client.clear_cache()
