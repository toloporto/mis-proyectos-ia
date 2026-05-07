.PHONY: setup run test

setup:
	python3 -m venv venv
	. venv/bin/activate && pip install -r requirements.txt

run:
	venv/bin/uvicorn app.main:api --reload --host 0.0.0.0 --port 8000

test:
	venv/bin/pytest tests/ -v
