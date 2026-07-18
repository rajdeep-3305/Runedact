from typing import Any, Dict

# Shared test harness appended to each submission. The student's function is
# called once per test case and the results are printed as JSON on the last
# line, which the sandbox parses back.
HARNESS_TEMPLATE = """
import json

if __name__ == '__main__':
    test_cases = {test_cases_json}
    results = []
    for i, tc in enumerate(test_cases):
        try:
            res = {entry_point}(**tc['input'])
            passed = ({compare_res}) == ({compare_expected})
            results.append({{'test_idx': i, 'passed': passed, 'got': res, 'expected': tc['expected'], 'hidden': tc.get('hidden', False)}})
        except MemoryError:
            results.append({{'test_idx': i, 'passed': False, 'error': 'MemoryError: address space limit exceeded', 'hidden': tc.get('hidden', False)}})
        except Exception as e:
            err_text = f'{{type(e).__name__}}: {{e}}' if str(e) else type(e).__name__
            results.append({{'test_idx': i, 'passed': False, 'error': err_text, 'hidden': tc.get('hidden', False)}})
    print(json.dumps(results))
"""

TWO_SUM_STARTER = (
    "def two_sum(nums: list[int], target: int) -> list[int]:\n"
    "    # Write your solution here\n"
    "    pass\n"
)

VALID_PARENTHESES_STARTER = (
    "def is_valid(s: str) -> bool:\n"
    "    # Write your solution here\n"
    "    pass\n"
)

COIN_CHANGE_STARTER = (
    "def coin_change(coins: list[int], amount: int) -> int:\n"
    "    # Write your solution here\n"
    "    pass\n"
)

PROBLEMS: Dict[str, Dict[str, Any]] = {
    "two-sum": {
        "id": "two-sum",
        "title": "Two Sum",
        "difficulty": "Easy",
        "tags": ["Array", "Hash Table"],
        "description": (
            "Given an array of integers `nums` and an integer `target`, return indices of the two numbers "
            "such that they add up to `target`.\n\n"
            "You may assume that each input would have exactly one solution, and you may not use the same element twice.\n"
            "You can return the answer in any order."
        ),
        "constraints": [
            "2 <= nums.length <= 10^4",
            "-10^9 <= nums[i] <= 10^9",
            "-10^9 <= target <= 10^9",
            "Only one valid answer exists.",
        ],
        "starter_code": {"python": TWO_SUM_STARTER},
        "test_cases": (test_cases := [
            {"input": {"nums": [2, 7, 11, 15], "target": 9}, "expected": [0, 1], "hidden": False},
            {"input": {"nums": [3, 2, 4], "target": 6}, "expected": [1, 2], "hidden": False},
            {"input": {"nums": [3, 3], "target": 6}, "expected": [0, 1], "hidden": False},
            {"input": {"nums": [-1, -2, -3, -4, -5], "target": -8}, "expected": [2, 4], "hidden": True},
            {"input": {"nums": [0, 4, 3, 0], "target": 0}, "expected": [0, 3], "hidden": True},
        ]),
        # answers in any order, so compare sorted indices
        "harness_code": HARNESS_TEMPLATE.format(
            test_cases_json=repr(test_cases),
            entry_point="two_sum",
            compare_res="sorted(res) if isinstance(res, list) else res",
            compare_expected="sorted(tc['expected'])",
        ),
    },
    "valid-parentheses": {
        "id": "valid-parentheses",
        "title": "Valid Parentheses",
        "difficulty": "Easy",
        "tags": ["String", "Stack"],
        "description": (
            "Given a string `s` containing just the characters `'('`, `')'`, `'{'`, `'}'`, `'['` and `']'`, "
            "determine if the input string is valid.\n\n"
            "An input string is valid if:\n"
            "1. Open brackets must be closed by the same type of brackets.\n"
            "2. Open brackets must be closed in the correct order.\n"
            "3. Every close bracket has a corresponding open bracket of the same type."
        ),
        "constraints": [
            "1 <= s.length <= 10^4",
            "s consists of parentheses only '()[]{}'.",
        ],
        "starter_code": {"python": VALID_PARENTHESES_STARTER},
        "test_cases": (test_cases := [
            {"input": {"s": "()"}, "expected": True, "hidden": False},
            {"input": {"s": "()[]{}"}, "expected": True, "hidden": False},
            {"input": {"s": "(]"}, "expected": False, "hidden": False},
            {"input": {"s": "([)]"}, "expected": False, "hidden": False},
            {"input": {"s": "{[]}"}, "expected": True, "hidden": True},
            {"input": {"s": "((((("}, "expected": False, "hidden": True},
            {"input": {"s": "))))"}, "expected": False, "hidden": True},
        ]),
        "harness_code": HARNESS_TEMPLATE.format(
            test_cases_json=repr(test_cases),
            entry_point="is_valid",
            compare_res="res",
            compare_expected="tc['expected']",
        ),
    },
    "coin-change": {
        "id": "coin-change",
        "title": "Coin Change",
        "difficulty": "Medium",
        "tags": ["Dynamic Programming", "Array"],
        "description": (
            "You are given an integer array `coins` representing coins of different denominations and an integer `amount` "
            "representing a total amount of money.\n\n"
            "Return the fewest number of coins that you need to make up that amount. If that amount of money cannot be "
            "made up by any combination of the coins, return `-1`.\n\n"
            "You may assume that you have an infinite number of each kind of coin."
        ),
        "constraints": [
            "1 <= coins.length <= 12",
            "1 <= coins[i] <= 2^31 - 1",
            "0 <= amount <= 10^4",
        ],
        "starter_code": {"python": COIN_CHANGE_STARTER},
        "test_cases": (test_cases := [
            {"input": {"coins": [1, 2, 5], "amount": 11}, "expected": 3, "hidden": False},
            {"input": {"coins": [2], "amount": 3}, "expected": -1, "hidden": False},
            {"input": {"coins": [1], "amount": 0}, "expected": 0, "hidden": False},
            {"input": {"coins": [1, 3, 4], "amount": 6}, "expected": 2, "hidden": False},
            {"input": {"coins": [2, 5, 10, 1], "amount": 27}, "expected": 4, "hidden": True},
        ]),
        "harness_code": HARNESS_TEMPLATE.format(
            test_cases_json=repr(test_cases),
            entry_point="coin_change",
            compare_res="res",
            compare_expected="tc['expected']",
        ),
    },
}
