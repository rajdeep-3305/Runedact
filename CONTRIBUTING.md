# Contributing

## Setup

```bash
git clone https://github.com/rajdeep-3305/Runedact.git
cd Runedact
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements.txt
cd frontend && npm install && cd ..
```

## Development

```bash
# Backend with hot reload
source .venv/bin/activate
cd backend && uvicorn app.main:app --reload

# Frontend with hot reload
cd frontend && npm run dev
```

## Tests

```bash
.venv/bin/pytest backend/tests/ -v
```

## Commits

Use conventional commits, e.g. `feat(sandbox): cap wall-clock execution time`, `fix(ui): reset test tab after a new run`.
