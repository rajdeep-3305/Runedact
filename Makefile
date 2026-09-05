.PHONY: install run dev test lint clean

install:
	python3 -m venv .venv
	.venv/bin/pip install -r backend/requirements.txt

run:
	PYTHONPATH=backend .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000

dev:
	PYTHONPATH=backend .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

test:
	.venv/bin/pytest backend/tests/ -v

lint:
	.venv/bin/python -m compileall -q backend/app

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
