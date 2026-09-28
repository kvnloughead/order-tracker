.PHONY: setup
setup:
	python3 -m venv venv
	source venv/bin/activate
	pip install -r backend/requirements.txt

.PHONY: run
run:
	python -m backend.app

.PHONY: test/fast
test/fast:
	pytest -m "not api"

.PHONY: test/all
test/all:
	pytest

