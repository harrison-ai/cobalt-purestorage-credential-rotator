IMAGE_NAME ?= ghcr.io/harrison-ai/cobalt-purestorage-credentials-rotator
IMAGE_TAG ?= $(shell git rev-parse HEAD | cut -c1-8)

.EXPORT_ALL_VARIABLES:

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

clean: clean-build clean-pyc clean-test

build:
	docker compose build app

down:
	docker compose down --remove-orphans --volumes

# Auto-fix import order, then run ruff linter and formatter.
lint:
	uv run ruff check --select I --fix
	uv run ruff check
	uv run ruff format

# Check-only lint (no writes). Used in CI.
ci-lint:
	uv run ruff check --select I
	uv run ruff check
	uv run ruff format --check

publish:
	docker tag $(IMAGE_NAME):local $(IMAGE_NAME):$(IMAGE_TAG)
	docker push $(IMAGE_NAME):$(IMAGE_TAG)

publish-release:
	docker tag $(IMAGE_NAME):local $(IMAGE_NAME):$(IMAGE_TAG)
	docker tag $(IMAGE_NAME):local $(IMAGE_NAME):latest
	docker push $(IMAGE_NAME):$(IMAGE_TAG)
	docker push $(IMAGE_NAME):latest

requirements:
	uv export --format requirements-txt --no-dev --no-emit-project -o requirements.txt

rotate:
	docker compose up app

shell:
	docker compose run --rm --entrypoint='' app /bin/bash

smoketest:
	docker compose up smoketest

test:
	uv run pytest -sv
