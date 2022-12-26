 
format:
	poetry run black src tests --safe

lint:
	poetry run flake8 src tests

tests:
	poetry run pytest

# For production environment
run-organizations:
	python -m uvicorn src.organizations.main:app --port 80

run-gateway:
	python -m uvicorn src.gateway.main:app --port 80

# For dev environment
run-organizations-dev:
	@(export $(shell cat src/organizations/.env) && poetry run python -m uvicorn src.organizations.main:app --reload)

run-gateway-dev:
	@(export $(shell cat src/gateway/.env) && poetry run python -m uvicorn src.gateway.main:app --reload)