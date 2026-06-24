.PHONY: test lint run clean report check-lengths

test:
	uv run pytest tests/unit/ -v

test-all:
	uv run pytest tests/ -v

test-smoke:
	uv run pytest tests/integration/ -v -m "not integration"

lint:
	uv run ruff check src/ tests/
	uv run ruff format --check src/ tests/
	uv run mypy src/hw5/ --ignore-missing-imports
	find src -name "*.py" -exec awk 'END{if(NR>150) print FILENAME": "NR" lines (exceeds 150)"}' {} \;

format:
	uv run ruff format src/ tests/
	uv run ruff check --fix src/ tests/

type-check:
	uv run mypy src/hw5/

run:
	uv run python src/hw5/main.py --mode full

run-dry:
	uv run python src/hw5/main.py --mode full --dry-run

report:
	uv run python src/hw5/main.py --mode report

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .coverage htmlcov/ .pytest_cache/
	rm -f results/**/*.json assets/*.png assets/*.svg assets/*.html

check-lengths:
	@echo "Files over 150 lines:"
	@find src -name "*.py" -exec awk 'END{if(NR>150) print FILENAME": "NR" lines"}' {} \; | grep . || echo "None — all files within limit"
