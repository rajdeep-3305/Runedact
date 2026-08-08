# Architecture

## Overview

The app has 3 main parts:
- **Sandbox** — runs student code with resource limits
- **AST Analyzer** — parses the code to find complexity issues
- **Mentor** — generates AI hints based on the analysis

## Request Flow

1. Student submits code
2. The code runs in the sandbox (2s CPU, 64MB memory limit)
3. The AST analyzer checks for nested loops, recursion, etc.
4. The analyzer's verdict is looked up in the hint cache
5. On a miss, the LLM generates a hint
6. The leak guard verifies the hint doesn't contain the full solution
7. The response is sent back and cached

## Sandbox

Uses `resource.setrlimit` to limit CPU time, memory, and process count. This avoids the overhead of spinning up Docker containers for each submission.

> **Note**: This only limits resources. It doesn't provide filesystem or network isolation. For production use, you'd want something like Docker or Firecracker.

## AST Analysis

Parses submissions with Python's built-in `ast` module and extracts loop nesting depth, recursive calls, memoization usage, and common anti-patterns.

## Hint Cache

An in-memory dict keyed on (problem, hint level, sandbox status, analyzer verdict). Identical situations are served from memory instead of paying for another LLM call.

## Leak Guard

Scans LLM output with regex to catch:
- Full function definitions
- Multi-line code blocks
- Phrases like "here is the complete solution"

If caught, replaces the response with a generic hint.
