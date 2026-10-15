.PHONY: help install install-dev lint typecheck format check clean

help:
	@echo "EyeDx - Development commands (structure only)"
	@echo "Note: Not executed per phase rules"

install:
	@echo "pip install -r requirements.txt"

install-dev:
	@echo "pip install -e '.[dev]'"

lint:
	@echo "ruff check . && black --check . && mypy ."

format:
	@echo "ruff format . && black ."

typecheck:
	@mypy .

check: lint typecheck

clean:
	@find . -type d -name __pycache__ -exec rm -rf {} +
	@find . -name "*.pyc" -delete
