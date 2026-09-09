import time
from typing import Any, Dict

from app.core.config import settings

# keyword-matched hints, not from an LLM. i wrote these by hand after seeing
# the same bugs in my own code a dozen times — rough but hopefully useful
MOCK_HINTS: Dict[str, Dict[int, str]] = {
    "nested loop": {
        1: "btw your nested loop is going to be slow on the bigger test cases. "
        "for two-sum specifically, instead of checking every pair, think about "
        "looking up the complement in one pass using a dict.",
        2: "keep a `seen` dict as you walk through the array. at each number `n`, "
        "the value you want is `target - n` — if it's already in `seen`, return "
        "the indices. otherwise add this number to the dict.",
        3: "so the fix is: drop the inner loop. for i, n in enumerate(nums): "
        "complement = target - n; if complement in seen: return [seen[complement], i]; "
        "seen[n] = i. heads up — if the same number appears twice, the dict overwrites "
        "the earlier index. might not matter for two-sum but good to know.",
    },
    "time_limit_exceeded": {
        1: "your code ran past the 2s limit. is there a while loop that doesn't "
        "increment its counter, or are you recursing without a cache?",
        2: "check that every code path in your loop moves a pointer forward, "
        "and that every recursive branch hits a base case. if the subproblems "
        "overlap, you probably need memoization.",
        3: "timeout usually means infinite loop or exponential blowup. fix the "
        "loop condition first (make sure the variable changes), then add a "
        "cache to your recursion if it's branching.",
    },
    "valid parentheses": {
        1: "counting open and close brackets isn't enough — order matters. "
        "what data structure is last-in-first-out?",
        2: "push on opens, pop on closes. but check that the popped bracket "
        "actually matches the closing one — not just that the stack isn't empty.",
        3: "the classic footgun: stack.pop() on a leading ')' crashes. check "
        "len(stack) > 0 first. also don't forget to make sure the stack is "
        "empty at the end — extra opens slip through otherwise.",
    },
    "coin change": {
        1: "greedy doesn't work here — try coins=[1,3,4], amount=6. greedy picks "
        "4 first then needs 1+1, so 3 coins. but the answer is 2 (3+3). "
        "what approach checks all combos?",
        2: "this is a DP problem. the idea: min coins for amount `a` is "
        "1 + min(min_coins(a - coin) for coin in coins). you've seen this pattern.",
        3: "dp array of size amount+1, fill with amount+1 (avoids float('inf') "
        "edge case). dp[0] = 0. dp[a] = min(dp[a], 1 + dp[a - coin]). "
        "return dp[amount] if it's < amount+1, else -1.",
    },
}

# when nothing keyword-matches, still try to point you somewhere useful
# instead of just saying "try harder"
FALLBACK_HINTS = {
    1: "i haven't seen this exact bug before but let's figure it out. "
    "grab a pen and trace through your code on a tiny example — what does "
    "each variable hold after every step?",
    2: "look at the first failing test case. is your loop off by one, "
    "or are you forgetting to update some variable inside the loop?",
    3: "read the error message carefully — the traceback usually tells you "
    "exactly which line broke and what kind of error it was. "
    "don't just guess, fix the actual error.",
}


class BaseLLMProvider:
    def generate(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        raise NotImplementedError


class MockMentorProvider(BaseLLMProvider):

    def generate(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        start = time.perf_counter()
        lower_prompt = user_prompt.lower()

        hint_level = 1
        if "level 3" in lower_prompt:
            hint_level = 3
        elif "level 2" in lower_prompt:
            hint_level = 2

        content = FALLBACK_HINTS[hint_level]
        for keyword, hints in MOCK_HINTS.items():
            if keyword in lower_prompt:
                content = hints[hint_level]
                break

        return {
            "content": content,
            "provider": "mock",
            "latency_ms": round((time.perf_counter() - start) * 1000, 2),
        }


class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        from google import genai

        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def generate(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        start = time.perf_counter()
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=f"{system_prompt}\n\nUser Question and Context:\n{user_prompt}",
        )
        return {
            "content": response.text or "",
            "provider": f"gemini ({self.model_name})",
            "latency_ms": round((time.perf_counter() - start) * 1000, 2),
        }


class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini"):
        from openai import OpenAI

        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name

    def generate(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        start = time.perf_counter()
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.4,
        )
        return {
            "content": response.choices[0].message.content or "",
            "provider": f"openai ({self.model_name})",
            "latency_ms": round((time.perf_counter() - start) * 1000, 2),
        }


def get_llm_provider() -> BaseLLMProvider:
    provider = settings.LLM_PROVIDER.lower()

    candidates = []
    if provider == "gemini" and settings.GEMINI_API_KEY:
        candidates = [GeminiProvider]
    elif provider == "openai" and settings.OPENAI_API_KEY:
        candidates = [OpenAIProvider]
    elif provider == "auto":
        if settings.GEMINI_API_KEY:
            candidates.append(GeminiProvider)
        if settings.OPENAI_API_KEY:
            candidates.append(OpenAIProvider)

    for cls in candidates:
        try:
            if cls is GeminiProvider:
                return cls(settings.GEMINI_API_KEY, settings.GEMINI_MODEL)
            return cls(settings.OPENAI_API_KEY, settings.OPENAI_MODEL)
        except Exception:
            continue

    return MockMentorProvider()
