
from fastapi.testclient import TestClient

from app.leetcode.client import (
    LeetCodeError,
    extract_examples,
    html_to_text,
    leetcode_client,
)
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


TWO_SUM_CONTENT = (
    "<p>Given an array of integers <code>nums</code>.</p>"
    "<pre>Input: nums = [2,7,11,15], target = 9\nOutput: [0,1]</pre>"
    "<pre>Input: nums = [3,2,4], target = 6\nOutput: [1,2]</pre>"
)


def test_extract_examples_parses_input_output_pairs():
    examples = extract_examples(TWO_SUM_CONTENT)
    assert examples == [
        {"input": {"nums": [2, 7, 11, 15], "target": 9}, "expected": [0, 1]},
        {"input": {"nums": [3, 2, 4], "target": 6}, "expected": [1, 2]},
    ]


def test_extract_examples_skips_prose_outputs():
    markup = "<pre>Input: s = 3\nOutput: whatever the judge decides</pre>"
    assert extract_examples(markup) == []


def _stub_practice_question(monkeypatch, tags=None, content=TWO_SUM_CONTENT):
    def fake_post(query, variables):
        return {
            "questionData": {
                "questionFrontendId": "1",
                "title": "Two Sum",
                "titleSlug": "two-sum",
                "difficulty": "Easy",
                "isPaidOnly": False,
                "content": content,
                "hints": [],
                "topicTags": [{"name": t} for t in (tags or ["Array"])],
                "codeSnippets": [
                    {
                        "langSlug": "python3",
                        "code": (
                            "class Solution:\n"
                            "    def twoSum(self, nums: List[int], target: int) -> List[int]:\n"
                            "        pass"
                        ),
                    }
                ],
            }
        }

    monkeypatch.setattr("app.leetcode.client._graphql_post", fake_post)
    leetcode_client.clear_cache()


def test_practice_pack_wraps_class_solution(monkeypatch):
    _stub_practice_question(monkeypatch)
    pack = leetcode_client.practice("two-sum")
    assert pack["practice"] is not None
    assert pack["practice"]["entry_point"] == "Solution().twoSum"
    assert pack["practice"]["starter_code"].startswith("class Solution")
    # the harness calls through an instance; the class itself comes from the
    # student's code, which the executor prepends to the harness
    assert "Solution().twoSum(" in pack["practice"]["harness_code"]
    assert len(pack["practice"]["test_cases"]) == 2


def test_practice_pack_absent_for_tree_problems(monkeypatch):
    _stub_practice_question(monkeypatch, tags=["Tree", "Binary Search"])
    pack = leetcode_client.practice("some-tree")
    assert pack["practice"] is None


def test_practice_pack_absent_without_parsable_examples(monkeypatch):
    _stub_practice_question(monkeypatch, content="<p>Just prose, no examples.</p>")
    pack = leetcode_client.practice("prose-problem")
    assert pack["practice"] is None


def test_leetcode_run_endpoint_executes_pack(monkeypatch):
    _stub_practice_question(monkeypatch)
    res = client.post(
        "/api/v1/leetcode/two-sum/run",
        json={
            "slug": "two-sum",
            "code": (
                "class Solution:\n"
                "    def twoSum(self, nums, target):\n"
                "        seen = {}\n"
                "        for i, n in enumerate(nums):\n"
                "            if target - n in seen:\n"
                "                return [seen[target - n], i]\n"
                "            seen[n] = i\n"
            ),
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "accepted"
    assert body["passed_count"] == body["total_count"] == 2


def test_leetcode_run_rejects_unpracticable_problem(monkeypatch):
    _stub_practice_question(monkeypatch, content="<p>no examples here</p>")
    res = client.post(
        "/api/v1/leetcode/two-sum/run",
        json={"slug": "two-sum", "code": "class Solution:\n    pass"},
    )
    assert res.status_code == 422


def test_leetcode_run_rejects_slug_mismatch():
    res = client.post(
        "/api/v1/leetcode/two-sum/run",
        json={"slug": "other-slug", "code": "x = 1"},
    )
    assert res.status_code == 422


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
