 
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

run-gateway:
	python -m uvicorn src.gateway.main:app --port 80

# For dev environment
run-structures-dev:
	@(export $(shell cat src/structures/.env) && poetry run python -m uvicorn src.structures.main:app --reload)

run-gateway-dev:
	@(export $(shell cat src/gateway/.env) && poetry run python -m uvicorn src.gateway.main:app --reload)