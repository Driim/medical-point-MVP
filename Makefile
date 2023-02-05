 
format:
	poetry run isort src tests --profile black
	poetry run black src tests --safe

lint:
	poetry run flake8 src tests

testing:
	@(export $(shell cat tests/.env) && poetry run pytest $(ARGS))

# For production environment
run-structures:
	python -m uvicorn src.structures.main:app --port 80

# For dev environment
run-structures-dev:
	@(export $(shell cat src/structures/.env) && poetry run python -m uvicorn src.structures.main:app --reload)

run-generate-import:
	@(export PYTHONPATH="${PYTHONPATH}:$(pwd)" && poetry run python src/imports/build_import_files.py)

build:
	docker build -f src/containers/structures/Dockerfile -t org-structures .