# Runedact

Practice DSA out loud — get hints, never answers.

You write Python in the browser, it runs in a sandboxed subprocess with CPU
and memory limits, and the mentor gives you hints without handing over the
solution. No API keys required — the mentor falls back to a mock provider
that keyword-matches common bug patterns.

## What's in here

The sandbox runs your code in a subprocess with `setrlimit`: 2s CPU, 64MB RAM,
1 process. Fork bombs and `while True:` both die quietly. Your code is
temp-filed, executed, and torn down before you get the results back.

The AST analyzer walks your code with Python's stdlib `ast` module and flags
the usual suspects: nested loops, unmemoized recursion, `list.index()` inside
loops, that kind of thing. It also estimates big-O so the mentor prompt has
some context.

Hints come in 3 levels. Level 1 is a conceptual nudge, level 2 points at the
right data structure or invariant, level 3 is more targeted. You pick how
much help you want. Everything the LLM says goes through a leak guard first —
regex checks for code blocks, function/class defs, and phrases like "here is
the complete solution." If it trips, you get a generic fallback instead.

The hint cache is just a dict keyed on problem + hint level + analyzer verdict.
Same situation = same hint from memory, no second LLM call. It's in-memory
only though, so restarts clear it.

There's also a read-only LeetCode browser backed by their GraphQL API.
Imported problems run against the statement's example blocks only — not their
hidden test cases, which aren't public. That's by design.

## How it actually works

1. Your code + a test harness is written to a temp file and run as a
   subprocess. `preexec_fn` applies the rlimits before exec.
2. The AST walker checks for complexity smells.
3. Hint cache is checked — if it's a hit, we skip the LLM entirely.
4. On a miss, the LLM (Gemini/OpenAI, or mock fallback) gets a structured
   prompt with your code, AST metrics, and what the sandbox found.
5. Every LLM response goes through the leak guard before you see it.

## Getting it running

```bash
git clone https://github.com/rajdeep-3305/Runedact.git
cd Runedact
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements.txt
cd frontend && npm install && npm run build && cd ..
./start.sh
```

Then open http://localhost:8000.

You can also use the Makefile targets: `make install`, `make run`, `make dev`,
`make test`, `make lint`.

## API endpoints

- `GET  /api/v1/problems` — list problems
- `GET  /api/v1/problems/{id}` — full statement + starter code
- `POST /api/v1/run` — execute in sandbox
- `POST /api/v1/analyze` — AST only, no execution
- `POST /api/v1/mentor/hint` — get a leveled hint
- `POST /api/v1/evals/run` — run the eval benchmark
- `GET  /api/v1/evals/history` — past benchmark runs

## Sandbox limits

- CPU: 2s — `RLIMIT_CPU` + wall-clock timeout on the subprocess
- Memory: 64MB — `RLIMIT_AS`
- Processes: 1 — `RLIMIT_NPROC`

This only limits resources, not filesystem or network. For real isolation
you'd want containers. I haven't gotten around to that yet.

## Eval dataset

`backend/app/evals/dataset.json` has 7 buggy submissions covering the mistakes
you actually make: nested-loop brute force, duplicate index collision, counting
brackets instead of a stack, popping an empty stack, greedy failure, unmemoized
recursion, and infinite loop from a stuck pointer. The harness scores hints with
simple string matching — no external judge API.

## Known issues

- LeetCode import only works for problems with plain literal examples (no linked
  lists, trees, or graphs). The HTML parsing is fragile on premium problems.
- Hint cache is in-memory only — restarts lose everything.
- Mock hints only cover 4 problem types. Most bugs get a generic fallback.
- No user accounts yet.

## License

MIT.
