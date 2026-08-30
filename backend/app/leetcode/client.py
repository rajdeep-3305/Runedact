
import ast
import json
import re
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser
from typing import Any, Dict, List, Optional, Tuple

from app.sandbox.problems import HARNESS_TEMPLATE

GRAPHQL_URL = "https://leetcode.com/graphql"
PUBLIC_URL = "https://leetcode.com/problems/"

CATALOG_TTL_SECONDS = 6 * 3600
QUESTION_TTL_SECONDS = 24 * 3600
REQUEST_TIMEOUT_SECONDS = 10

CATALOG_QUERY = """
query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
  problemsetQuestionList: questionList(
    categorySlug: $categorySlug, limit: $limit, skip: $skip, filters: $filters
  ) {
    total: totalNum
    questions: data {
      questionFrontendId
      title
      titleSlug
      difficulty
      isPaidOnly
      topicTags { name }
    }
  }
}
"""

QUESTION_QUERY = """
query getQuestionDetail($titleSlug: String!) {
  questionData: question(titleSlug: $titleSlug) {
    questionFrontendId
    title
    titleSlug
    difficulty
    isPaidOnly
    content
    hints
    topicTags { name }
    codeSnippets { lang langSlug code }
  }
}
"""


class LeetCodeError(Exception):


class _HTMLToText(HTMLParser):

    _BLOCK_TAGS = {"p", "div", "ul", "ol", "h1", "h2", "h3", "h4", "table", "tr"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: List[str] = []
        self._in_pre = False

    def handle_starttag(self, tag: str, attrs: Any) -> None:
        if tag == "pre":
            self._in_pre = True
            self.parts.append("\n")
        elif tag == "br":
            self.parts.append("\n")
        elif tag == "li":
            self.parts.append("\n• ")
        elif tag in self._BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag == "pre":
            self._in_pre = False
            self.parts.append("\n")
        elif tag in self._BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._in_pre:
            self.parts.append(data)
            return
        # collapse internal whitespace but keep edge spaces, so text split
        # across inline tags ("array</code><code>nums") doesn't fuse together
        self.parts.append(re.sub(r"\s+", " ", data))


def html_to_text(markup: str) -> str:
    parser = _HTMLToText()
    parser.feed(markup)
    text = "".join(parser.parts)
    # collapse the blank runs the tag handling leaves behind
    lines = [line.rstrip() for line in text.splitlines()]
    text = "\n".join(lines)
    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")
    return text.strip()


def _graphql_post(query: str, variables: Dict[str, Any]) -> Dict[str, Any]:
    request = urllib.request.Request(
        GRAPHQL_URL,
        data=json.dumps({"query": query, "variables": variables}).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Referer": "https://leetcode.com",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) runedact/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise LeetCodeError(f"leetcode responded with HTTP {exc.code}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise LeetCodeError("could not reach leetcode") from exc

    if body.get("errors"):
        message = body["errors"][0].get("message", "graphql error")
        raise LeetCodeError(message)
    return body.get("data") or {}


# examples appear as "Input: ... / Output: ..." pairs inside pre blocks;
# matches must stop at the closing </pre> so markup never leaks into values
_INPUT_RE = re.compile(r"Input:\s*(.+?)(?=(?:Output|Explanation|Constraints|</pre>)|$)", re.DOTALL | re.IGNORECASE)
_OUTPUT_RE = re.compile(r"Output:\s*(.+?)(?=(?:Explanation|Constraints|Input|</pre>)|$)", re.DOTALL | re.IGNORECASE)
_TAG_RE = re.compile(r"<[^>]+>")
_ENTRY_POINT_RE = re.compile(r"def\s+([a-zA-Z_]\w*)\s*\(")

# problem shapes whose inputs are node/graph handles rather than plain python
# literals — the example parser can't build test data for them
_UNSUPPORTED_TAGS = {"linked-list", "tree", "binary-tree", "graph"}


def extract_examples(markup: str) -> List[Dict[str, Any]]:
    examples: List[Dict[str, Any]] = []
    inputs = [m.group(1).strip() for m in _INPUT_RE.finditer(markup)]
    outputs = [m.group(1).strip() for m in _OUTPUT_RE.finditer(markup)]
    for raw_in, raw_out in zip(inputs, outputs):
        params: Dict[str, Any] = {}
        ok = True
        for chunk in _split_params(raw_in):
            key, _, value = chunk.partition("=")
            try:
                params[key.strip()] = ast.literal_eval(value.strip())
            except (ValueError, SyntaxError):
                ok = False
                break
        if not ok or not params:
            continue
        try:
            expected = ast.literal_eval(_TAG_RE.sub("", raw_out).strip())
        except (ValueError, SyntaxError):
            continue
        examples.append({"input": params, "expected": expected})
    return examples


def _split_params(raw: str) -> List[str]:
    parts, depth, current = [], 0, []
    for ch in raw:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append("".join(current).strip())
            current = []
        else:
            current.append(ch)
    tail = "".join(current).strip()
    if tail:
        parts.append(tail)
    return parts


def _python_starter(code_snippets: List[Dict[str, Any]]) -> Optional[str]:
    for snippet in code_snippets or []:
        if snippet.get("langSlug") == "python3":
            return snippet.get("code") or ""
    return None


class LeetCodeClient:
    def __init__(self) -> None:
        self._catalog: Optional[List[Dict[str, Any]]] = None
        self._catalog_fetched_at: float = 0.0
        self._questions: Dict[str, Tuple[float, Dict[str, Any]]] = {}

    def clear_cache(self) -> None:
        self._catalog = None
        self._questions.clear()

    def catalog(self, limit: int = 50) -> List[Dict[str, Any]]:
        if self._catalog is None or time.time() - self._catalog_fetched_at > CATALOG_TTL_SECONDS:
            data = _graphql_post(
                CATALOG_QUERY,
                {"categorySlug": "", "skip": 0, "limit": 100, "filters": {}},
            )
            questions = (data.get("problemsetQuestionList") or {}).get("questions") or []
            self._catalog = [
                {
                    "id": q["titleSlug"],
                    "title": q["title"],
                    "difficulty": q["difficulty"],
                    "tags": [t["name"] for t in q.get("topicTags") or []],
                    "paid_only": bool(q.get("isPaidOnly")),
                }
                for q in questions
            ]
            self._catalog_fetched_at = time.time()
        return self._catalog[:limit]

    def question(self, slug: str) -> Dict[str, Any]:
        detail = self._question_detail(slug)
        return {
            "id": detail["id"],
            "title": detail["title"],
            "difficulty": detail["difficulty"],
            "tags": detail["tags"],
            "paid_only": detail["paid_only"],
            "description": detail["description"],
            "hints": detail["hints"],
        }

    def _question_detail(self, slug: str) -> Dict[str, Any]:
        cached = self._questions.get(slug)
        if cached and time.time() - cached[0] <= QUESTION_TTL_SECONDS:
            return cached[1]

        data = _graphql_post(QUESTION_QUERY, {"titleSlug": slug})
        q = data.get("questionData")
        if not q or not q.get("title"):
            raise LeetCodeError(f"no leetcode problem named '{slug}'")

        tags = [t["name"] for t in q.get("topicTags") or []]
        content = q.get("content") or ""
        starter = _python_starter(q.get("codeSnippets"))
        entry = _ENTRY_POINT_RE.search(starter or "")

        # a practice pack only exists when the shape supports it: plain python
        # literal inputs, parsed examples, and a known python entry point
        examples = extract_examples(content) if content else []
        unsupported = bool(_UNSUPPORTED_TAGS & {t.lower() for t in tags})
        practice_ready = bool(examples) and not unsupported and entry is not None and starter
        practice_pack: Optional[Dict[str, Any]] = None
        if practice_ready:
            # leetcode snippets wrap the entry point in `class Solution` with
            # a self parameter — keep them verbatim and call through an
            # instance, the same shape students see on leetcode itself
            if re.search(r"class\s+Solution\b", starter):
                call_target = f"Solution().{entry.group(1)}"
            else:
                call_target = entry.group(1)
            test_cases = [
                {"input": ex["input"], "expected": ex["expected"], "hidden": False}
                for ex in examples
            ]
            practice_pack = {
                "entry_point": call_target,
                "starter_code": starter,
                "test_cases": test_cases,
                # the typing prelude mirrors leetcode's default imports; their
                # snippets annotate with List/Optional without importing them
                "harness_code": (
                    "from typing import List, Optional, Dict, Tuple\n\n\n"
                    + HARNESS_TEMPLATE.format(
                        test_cases_json=repr(test_cases),
                        entry_point=call_target,
                        compare_res="res",
                        compare_expected="tc['expected']",
                    )
                ),
            }

        detail = {
            "id": q["titleSlug"],
            "title": q["title"],
            "difficulty": q["difficulty"],
            "tags": tags,
            "paid_only": bool(q.get("isPaidOnly")),
            # premium problems come back with content=None
            "description": html_to_text(content) if content else "",
            "hints": [h for h in q.get("hints") or [] if h],
            "practice": practice_pack,
        }
        self._questions[slug] = (time.time(), detail)
        return detail

    def practice(self, slug: str) -> Dict[str, Any]:
        detail = self._question_detail(slug)
        return {
            "id": detail["id"],
            "title": detail["title"],
            "difficulty": detail["difficulty"],
            "tags": detail["tags"],
            "paid_only": detail["paid_only"],
            "description": detail["description"],
            "hints": detail["hints"],
            "practice": detail["practice"],
            "constraints": [],
        }


leetcode_client = LeetCodeClient()
