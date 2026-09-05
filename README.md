# Runedact

Practice DSA out loud — get hints, never answers.

Your Python runs in a resource-limited sandbox, you see what happens, and a
mentor gives hints without handing over the solution.

## What it does

- **Sandbox** — submissions run in a subprocess under `setrlimit` (2s CPU, 64MB
  RAM, 1 process). Fork bombs and `while True:` both die quietly.
- **AST analysis** — walks your code with Python's stdlib `ast` module, flags
  nested loops, unmemoized recursion, and `list.index()` inside loops.
- **Leveled hints** — 3 levels: conceptual nudge, algorithmic direction, or
  targeted fix. You pick how much help to get.
- **Leak guard** — catches code blocks, function defs, and "here's the full
  solution" phrasing in LLM responses before they reach you.
- **Hint cache** — same situation = same hint from memory. No second LLM call.
- **LeetCode browser** — read-only catalog from their GraphQL API. Imported
  problems run against statement examples in the sandbox (examples-only).

## How it works

1. Your code + a test harness is written to a temp file, run as a subprocess
   with rlimits via `preexec_fn`.
2. The AST walker checks for complexity smells.
3. Hint cache is checked — if it's a hit, skip the LLM entirely.
4. On a miss, the LLM (Gemini/OpenAI, or a mock fallback) gets a structured
   prompt with your code, AST metrics, and what the sandbox found.
5. Every LLM response goes through LeakGuard before you see it.

## Quick start

```bash
git clone https://github.com/rajdeep-3305/Runedact.git
cd Runedact
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements.txt
cd frontend && npm install && npm run build && cd ..
./start.sh
```

Open http://localhost:8000. No API keys needed — the mentor falls back to a mock
provider that keyword-matches common bug patterns.

## API

| Method | Route | What |
|--------|-------|------|
| GET | /api/v1/problems | List problems |
| GET | /api/v1/problems/{id} | Full statement + starter code |
| POST | /api/v1/run | Execute in sandbox |
| POST | /api/v1/analyze | AST-only, no execution |
| POST | /api/v1/mentor/hint | Get a leveled hint |
| POST | /api/v1/evals/run | Run benchmark |
| GET | /api/v1/evals/history | Past benchmark runs |

## Sandbox limits

| Resource | Limit | How |
|----------|-------|-----|
| CPU | 2s | RLIMIT_CPU + wall-clock timeout |
| Memory | 64MB | RLIMIT_AS |
| Processes | 1 | RLIMIT_NPROC |

> Honest note: this only limits resources, not filesystem or network. For real
> isolation you'd want containers. I haven't gotten around to that yet.

## Eval dataset

`backend/app/evals/dataset.json` has 7 buggy submissions covering the mistakes
you actually make: nested-loop brute force, duplicate index collision, counting
brackets instead of a stack, popping an empty stack, greedy failure, unmemoized
recursion, and infinite loop from a stuck pointer. The harness scores hints with
simple string matching — no external APIs.

## Known issues

- LeetCode import only works for problems with plain literal examples (no linked
  lists, trees, or graphs). The HTML parsing is fragile on premium problems.
- Hint cache is in-memory only — restarts lose everything.
- Mock hints only cover 4 problem types. Most bugs get a generic fallback.
- No user accounts yet.

## License

MIT.
