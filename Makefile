 
format:
	poetry run isort src tests --profile black
	poetry run black src tests --safe

lint:
	poetry run flake8 src tests

testing:
	@(export $(shell cat tests/.env) && poetry run pytest $(ARGS))

# For production environment
run-structures:
	@(export $(shell cat src/structures/.env) && poetry run python -m gunicorn src.structures.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:80)

# For dev environment
run-structures-dev:
	@(export $(shell cat src/structures/.env) && poetry run python -m uvicorn src.structures.main:app --reload)

run-inspections-dev:
	@(export $(shell cat src/inspections/.env) && poetry run python -m uvicorn src.inspections.main:app --reload)

run-generate-import:
	@(export PYTHONPATH="${PYTHONPATH}:$(pwd)" && poetry run python src/imports/build_import_files.py)

run-generate-post-ammo:
	@(export PYTHONPATH="${PYTHONPATH}:$(pwd)" && poetry run python src/imports/ammo_generator.py > ammo.txt)

build:
	docker build -f src/containers/structures/Dockerfile -t cr.yandex/crpqf6q24glns01tar7l/org-structures:latest .

push:
	docker push cr.yandex/crpqf6q24glns01tar7l/org-structures:latest