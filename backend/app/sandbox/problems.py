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


def _starter(signature: str) -> str:
    return f"def {signature}:\n    # Write your solution here\n    pass\n"


TWO_SUM_STARTER = _starter("two_sum(nums: list[int], target: int) -> list[int]")
VALID_PARENTHESES_STARTER = _starter("is_valid(s: str) -> bool")
COIN_CHANGE_STARTER = _starter("coin_change(coins: list[int], amount: int) -> int")
REVERSE_INTEGER_STARTER = _starter("reverse_integer(x: int) -> int")
BINARY_SEARCH_STARTER = _starter("binary_search(nums: list[int], target: int) -> int")
MERGE_LISTS_STARTER = _starter("merge_two_sorted_lists(list1: list[int], list2: list[int]) -> list[int]")
LONGEST_SUBSTRING_STARTER = _starter("length_of_longest_substring(s: str) -> int")
CONTAINER_WATER_STARTER = _starter("max_area(height: list[int]) -> int")
ROTATE_ARRAY_STARTER = _starter("rotate_array(nums: list[int], k: int) -> list[int]")
MAX_SUBARRAY_STARTER = _starter("max_sub_array(nums: list[int]) -> int")
MERGE_INTERVALS_STARTER = _starter("merge(intervals: list[list[int]]) -> list[list[int]]")
TRAPPING_WATER_STARTER = _starter("trap(height: list[int]) -> int")

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
        # need test_cases for the harness template too, so re-use it with :=
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
    "reverse-integer": {
        "id": "reverse-integer",
        "title": "Reverse Integer",
        "difficulty": "Easy",
        "tags": ["Math"],
        "description": (
            "Given a signed 32-bit integer `x`, return `x` with its digits reversed. "
            "If reversing `x` causes the value to go outside the signed 32-bit integer range "
            "`[-2^31, 2^31 - 1]`, then return `0`.\n\n"
            "Assume the environment does not allow you to store 64-bit integers (signed or unsigned)."
        ),
        "constraints": [
            "-2^31 <= x <= 2^31 - 1",
        ],
        "starter_code": {"python": REVERSE_INTEGER_STARTER},
        "test_cases": (test_cases := [
            {"input": {"x": 123}, "expected": 321, "hidden": False},
            {"input": {"x": -123}, "expected": -321, "hidden": False},
            {"input": {"x": 120}, "expected": 21, "hidden": False},
            {"input": {"x": 1534236469}, "expected": 0, "hidden": True},
            {"input": {"x": -2147483648}, "expected": 0, "hidden": True},
        ]),
        "harness_code": HARNESS_TEMPLATE.format(
            test_cases_json=repr(test_cases),
            entry_point="reverse_integer",
            compare_res="res",
            compare_expected="tc['expected']",
        ),
    },
    "binary-search": {
        "id": "binary-search",
        "title": "Binary Search",
        "difficulty": "Easy",
        "tags": ["Array", "Binary Search"],
        "description": (
            "Given an array of integers `nums` which is sorted in ascending order, and an integer `target`, "
            "write a function to search `target` in `nums`. If `target` exists, then return its index, "
            "otherwise return `-1`.\n\n"
            "You must write an algorithm with `O(log n)` runtime complexity."
        ),
        "constraints": [
            "1 <= nums.length <= 10^4",
            "-10^4 < nums[i], target < 10^4",
            "All the integers in nums are unique.",
            "nums is sorted in ascending order.",
        ],
        "starter_code": {"python": BINARY_SEARCH_STARTER},
        "test_cases": (test_cases := [
            {"input": {"nums": [-1, 0, 3, 5, 9, 12], "target": 9}, "expected": 4, "hidden": False},
            {"input": {"nums": [-1, 0, 3, 5, 9, 12], "target": 2}, "expected": -1, "hidden": False},
            {"input": {"nums": [5], "target": 5}, "expected": 0, "hidden": False},
            {"input": {"nums": [5], "target": -5}, "expected": -1, "hidden": True},
            {"input": {"nums": [1, 3, 5, 7, 9, 11, 13], "target": 13}, "expected": 6, "hidden": True},
        ]),
        "harness_code": HARNESS_TEMPLATE.format(
            test_cases_json=repr(test_cases),
            entry_point="binary_search",
            compare_res="res",
            compare_expected="tc['expected']",
        ),
    },
    "merge-two-sorted-lists": {
        "id": "merge-two-sorted-lists",
        "title": "Merge Two Sorted Lists",
        "difficulty": "Easy",
        "tags": ["Linked List", "Recursion"],
        "description": (
            "You are given the heads of two sorted linked lists as plain Python lists, `list1` and `list2`.\n\n"
            "Merge the two lists into one sorted list (as a Python list) and return it. "
            "The list should be made by splicing together the nodes of the first two lists — "
            "in this formulation, just return the merged values."
        ),
        "constraints": [
            "0 <= list1.length, list2.length <= 50",
            "-100 <= list1[i], list2[i] <= 100",
            "list1 and list2 are sorted in non-decreasing order.",
        ],
        "starter_code": {"python": MERGE_LISTS_STARTER},
        "test_cases": (test_cases := [
            {"input": {"list1": [1, 2, 4], "list2": [1, 3, 4]}, "expected": [1, 1, 2, 3, 4, 4], "hidden": False},
            {"input": {"list1": [], "list2": [0]}, "expected": [0], "hidden": False},
            {"input": {"list1": [1, 5, 9], "list2": [2, 3]}, "expected": [1, 2, 3, 5, 9], "hidden": False},
            {"input": {"list1": [], "list2": []}, "expected": [], "hidden": True},
            {"input": {"list1": [-10, -3], "list2": [-7]}, "expected": [-10, -7, -3], "hidden": True},
        ]),
        "harness_code": HARNESS_TEMPLATE.format(
            test_cases_json=repr(test_cases),
            entry_point="merge_two_sorted_lists",
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
            {"input": {"coins": [186, 419, 83, 408], "amount": 6249}, "expected": 20, "hidden": True},
        ]),
        "harness_code": HARNESS_TEMPLATE.format(
            test_cases_json=repr(test_cases),
            entry_point="coin_change",
            compare_res="res",
            compare_expected="tc['expected']",
        ),
    },
    "longest-substring-without-repeating-characters": {
        "id": "longest-substring-without-repeating-characters",
        "title": "Longest Substring Without Repeating Characters",
        "difficulty": "Medium",
        "tags": ["String", "Sliding Window", "Hash Table"],
        "description": (
            "Given a string `s`, find the length of the longest substring without repeating characters.\n\n"
            "Note that the answer is a substring, not a subsequence."
        ),
        "constraints": [
            "0 <= s.length <= 5 * 10^4",
            "s consists of English letters, digits, symbols and spaces.",
        ],
        "starter_code": {"python": LONGEST_SUBSTRING_STARTER},
        "test_cases": (test_cases := [
            {"input": {"s": "abcabcbb"}, "expected": 3, "hidden": False},
            {"input": {"s": "bbbbb"}, "expected": 1, "hidden": False},
            {"input": {"s": "pwwkew"}, "expected": 3, "hidden": False},
            {"input": {"s": ""}, "expected": 0, "hidden": True},
            {"input": {"s": "dvdf"}, "expected": 3, "hidden": True},
            {"input": {"s": "abba"}, "expected": 2, "hidden": True},
        ]),
        "harness_code": HARNESS_TEMPLATE.format(
            test_cases_json=repr(test_cases),
            entry_point="length_of_longest_substring",
            compare_res="res",
            compare_expected="tc['expected']",
        ),
    },
    "container-with-most-water": {
        "id": "container-with-most-water",
        "title": "Container With Most Water",
        "difficulty": "Medium",
        "tags": ["Array", "Two Pointers"],
        "description": (
            "You are given an integer array `height` of length `n`. There are `n` vertical lines drawn such that "
            "the two endpoints of the `i`-th line are `(i, 0)` and `(i, height[i])`.\n\n"
            "Find two lines that together with the x-axis form a container, such that the container contains "
            "the most water, and return the maximum amount of water a container can store.\n\n"
            "Notice that you may not slant the container."
        ),
        "constraints": [
            "n == height.length",
            "2 <= n <= 10^5",
            "0 <= height[i] <= 10^4",
        ],
        "starter_code": {"python": CONTAINER_WATER_STARTER},
        "test_cases": (test_cases := [
            {"input": {"height": [1, 8, 6, 2, 5, 4, 8, 3, 7]}, "expected": 49, "hidden": False},
            {"input": {"height": [1, 1]}, "expected": 1, "hidden": False},
            {"input": {"height": [2, 3, 4, 5, 18, 17, 6]}, "expected": 17, "hidden": False},
            {"input": {"height": [4, 3, 2, 1, 4]}, "expected": 16, "hidden": True},
            {"input": {"height": [1, 2, 1]}, "expected": 2, "hidden": True},
        ]),
        "harness_code": HARNESS_TEMPLATE.format(
            test_cases_json=repr(test_cases),
            entry_point="max_area",
            compare_res="res",
            compare_expected="tc['expected']",
        ),
    },
    "rotate-array": {
        "id": "rotate-array",
        "title": "Rotate Array",
        "difficulty": "Medium",
        "tags": ["Array", "Math", "Two Pointers"],
        "description": (
            "Given an integer array `nums`, rotate the array to the right by `k` steps, where `k` is non-negative. "
            "Return the rotated array.\n\n"
            "For example, `[1, 2, 3, 4, 5, 6, 7]` rotated right by 3 becomes `[5, 6, 7, 1, 2, 3, 4]`."
        ),
        "constraints": [
            "1 <= nums.length <= 10^5",
            "-2^31 <= nums[i] <= 2^31 - 1",
            "0 <= k <= 10^5",
            "Try it without using extra space if you can.",
        ],
        "starter_code": {"python": ROTATE_ARRAY_STARTER},
        "test_cases": (test_cases := [
            {"input": {"nums": [1, 2, 3, 4, 5, 6, 7], "k": 3}, "expected": [5, 6, 7, 1, 2, 3, 4], "hidden": False},
            {"input": {"nums": [-1, -100, 3, 99], "k": 2}, "expected": [3, 99, -1, -100], "hidden": False},
            {"input": {"nums": [1, 2, 3], "k": 0}, "expected": [1, 2, 3], "hidden": False},
            {"input": {"nums": [1, 2], "k": 5}, "expected": [2, 1], "hidden": True},
            {"input": {"nums": [1, 2, 3, 4], "k": 4}, "expected": [1, 2, 3, 4], "hidden": True},
        ]),
        "harness_code": HARNESS_TEMPLATE.format(
            test_cases_json=repr(test_cases),
            entry_point="rotate_array",
            compare_res="res",
            compare_expected="tc['expected']",
        ),
    },
    "maximum-subarray": {
        "id": "maximum-subarray",
        "title": "Maximum Subarray",
        "difficulty": "Medium",
        "tags": ["Array", "Dynamic Programming"],
        "description": (
            "Given an integer array `nums`, find the subarray with the largest sum, and return its sum.\n\n"
            "A subarray is a contiguous non-empty sequence of elements within the array."
        ),
        "constraints": [
            "1 <= nums.length <= 10^5",
            "-10^4 <= nums[i] <= 10^4",
        ],
        "starter_code": {"python": MAX_SUBARRAY_STARTER},
        "test_cases": (test_cases := [
            {"input": {"nums": [-2, 1, -3, 4, -1, 2, 1, -5, 4]}, "expected": 6, "hidden": False},
            {"input": {"nums": [1]}, "expected": 1, "hidden": False},
            {"input": {"nums": [5, 4, -1, 7, 8]}, "expected": 23, "hidden": False},
            {"input": {"nums": [-1]}, "expected": -1, "hidden": True},
            {"input": {"nums": [-2, -1]}, "expected": -1, "hidden": True},
        ]),
        "harness_code": HARNESS_TEMPLATE.format(
            test_cases_json=repr(test_cases),
            entry_point="max_sub_array",
            compare_res="res",
            compare_expected="tc['expected']",
        ),
    },
    "merge-intervals": {
        "id": "merge-intervals",
        "title": "Merge Intervals",
        "difficulty": "Medium",
        "tags": ["Array", "Sorting"],
        "description": (
            "Given an array of `intervals` where `intervals[i] = [start_i, end_i]`, merge all overlapping intervals, "
            "and return an array of the non-overlapping intervals that cover all the intervals in the input.\n\n"
            "Two intervals `[a, b]` and `[b, c]` (touching endpoints) count as overlapping and should be merged. "
            "Return the merged intervals sorted by their start."
        ),
        "constraints": [
            "1 <= intervals.length <= 10^4",
            "intervals[i].length == 2",
            "0 <= start_i <= end_i <= 10^4",
        ],
        "starter_code": {"python": MERGE_INTERVALS_STARTER},
        "test_cases": (test_cases := [
            {"input": {"intervals": [[1, 3], [2, 6], [8, 10], [15, 18]]}, "expected": [[1, 6], [8, 10], [15, 18]], "hidden": False},
            {"input": {"intervals": [[1, 4], [4, 5]]}, "expected": [[1, 5]], "hidden": False},
            {"input": {"intervals": [[1, 4], [0, 4]]}, "expected": [[0, 4]], "hidden": False},
            {"input": {"intervals": [[1, 4], [2, 3]]}, "expected": [[1, 4]], "hidden": True},
            {"input": {"intervals": [[2, 2], [2, 2], [3, 5]]}, "expected": [[2, 2], [3, 5]], "hidden": True},
        ]),
        # merged intervals may come back in any order, so compare sorted
        "harness_code": HARNESS_TEMPLATE.format(
            test_cases_json=repr(test_cases),
            entry_point="merge",
            compare_res="sorted(res) if isinstance(res, list) else res",
            compare_expected="sorted(tc['expected'])",
        ),
    },
    "trapping-rain-water": {
        "id": "trapping-rain-water",
        "title": "Trapping Rain Water",
        "difficulty": "Hard",
        "tags": ["Array", "Two Pointers", "Dynamic Programming", "Stack"],
        "description": (
            "Given `n` non-negative integers representing an elevation map where the width of each bar is `1`, "
            "compute how much water it can trap after raining."
        ),
        "constraints": [
            "1 <= height.length <= 2 * 10^4",
            "0 <= height[i] <= 10^5",
        ],
        "starter_code": {"python": TRAPPING_WATER_STARTER},
        "test_cases": (test_cases := [
            {"input": {"height": [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]}, "expected": 6, "hidden": False},
            {"input": {"height": [4, 2, 0, 3, 2, 5]}, "expected": 9, "hidden": False},
            {"input": {"height": [3, 0, 3]}, "expected": 3, "hidden": False},
            {"input": {"height": [1, 2, 3, 4, 5]}, "expected": 0, "hidden": True},
            {"input": {"height": [5, 4, 3, 2, 1]}, "expected": 0, "hidden": True},
        ]),
        "harness_code": HARNESS_TEMPLATE.format(
            test_cases_json=repr(test_cases),
            entry_point="trap",
            compare_res="res",
            compare_expected="tc['expected']",
        ),
    },
}
