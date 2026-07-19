import time
from typing import Any, Dict

from app.core.config import settings

# keyword that identifies the situation in the built prompt -> hint per level
MOCK_HINTS: Dict[str, Dict[int, str]] = {
    "nested loop detected": {
        1: "Notice your nested loop scanning pairs. While this works for small inputs, "
        "what is the time complexity when the input array grows to 10,000 numbers? "
        "Can you think of a data structure that offers instantaneous O(1) lookups?",
        2: "As you iterate through each number `n`, the value you need to find is `complement = target - n`. "
        "If you store previously visited numbers in a Hash Map (dictionary), how can you check for the complement in O(1) time?",
        3: "Look at your inner loop: instead of searching the remainder of the array every time, "
        "check if `target - num` is already in your `seen` map. If yes, return indices immediately; "
        "otherwise, store `seen[num] = i`. What happens if the array has duplicates?",
    },
    "time limit exceeded": {
        1: "Your solution timed out on large test cases! What loop or recursion condition might be "
        "failing to terminate or repeating calculations over and over?",
        2: "Check your loop termination or recursion state. Are you advancing your pointers on every iteration, "
        "or recalculating overlapping subproblems without memoization?",
        3: "You hit the execution timeout. Look closely at your while loop condition or recursion base cases. "
        "Ensure your state variables strictly make progress towards termination.",
    },
    "valid parentheses": {
        1: "Parentheses must match in a Last-In, First-Out order. What classic data structure represents LIFO order?",
        2: "When you encounter an opening bracket like '(', you wait for its match. When you see a closing bracket ')', "
        "which opening bracket should it match with? How does a Stack help here?",
        3: "Consider edge cases: what happens if the string begins with a closing bracket ')' or has odd length? "
        "Ensure you check if the stack is non-empty before calling `stack.pop()`!",
    },
    "coin change": {
        1: "If you always pick the largest coin first (greedy), does it always yield the minimum coins for coins=[1, 3, 4] and amount=6? "
        "Try working that case out by hand!",
        2: "Since greedy choices can lead to suboptimal outcomes, we need to consider subproblems: "
        "To make `amount`, what is the relationship with `dp[amount - coin] + 1`?",
        3: "Initialize a DP array of size `amount + 1` filled with infinity, and `dp[0] = 0`. "
        "Iterate through each amount from 1 to `target`. For each coin, if `c <= a`, `dp[a] = min(dp[a], 1 + dp[a - c])`.",
    },
}

FALLBACK_HINTS = {
    1: "Let's trace your code on a small example. What is the state of your variables after the first step? "
    "Does your output match what the problem expects for the base case?",
    2: "Look at the failing test case. Is the issue in how you maintain your invariant or an off-by-one boundary condition?",
    3: "Check the return value when no valid answer is found, or when the input is empty or singular. "
    "What specific line causes the unexpected output?",
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
