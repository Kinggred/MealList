VENV := .venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
ALEMBIC := $(VENV)/bin/alembic
UVICORN := $(VENV)/bin/fastapi

venv:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip

install: venv
	$(PIP) install -r requirements.txt

dev:
	$(PY) -m fastapi dev app/api/main.py

freeze:
	$(PIP) freeze > requirements.txt

migrate_up:
	$(ALEMBIC) -c app/alembic.ini upgrade head

migrate:
	@read -p "Migration message: " msg; \
	$(ALEMBIC) -c app/alembic.ini revision --autogenerate -m "$$msg"

cleanup:
	$(VENV)/bin/black .