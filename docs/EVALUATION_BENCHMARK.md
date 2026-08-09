# Evaluation Benchmark

## Why

LLMs tend to just give away the answer when asked for help. We needed a way to measure if our hints are actually helpful without leaking solutions.

## Dataset

7 curated cases covering common DSA bug types:
- Nested loop brute force (should use hash map)
- Duplicate index collision
- Using counter instead of stack
- Empty stack pop
- Greedy approach failing
- Missing memoization in recursion
- Infinite loop (missing pointer advance)

## Metrics

- **Leak Rate**: does the hint contain actual code? Target: 0%
- **Quality Score**: is it asking questions? Is it concise?
- **Faithfulness**: is the hint grounded in the actual code analysis?
- **Relevance**: does it mention the right concepts?
- **Recall**: does it cover the key ideas?

All metrics are computed locally with string matching and regex — no external APIs needed.

## Running

```bash
.venv/bin/python backend/run_evals.py
```
