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

build-dev:
	docker compose build dev

build-app:
	docker compose build app

fmt:
	docker compose run --rm dev ./scripts/check.sh

test:
	docker compose run --rm dev ./scripts/test.sh

shell:
	docker compose run --rm --entrypoint='' dev /bin/bash

rotate:
	docker compose up app

smoketest:
	docker compose up smoketest

down:
	docker compose down --remove-orphans --volumes

publish:
	docker tag $(IMAGE_NAME):local $(IMAGE_NAME):$(IMAGE_TAG)
	docker push $(IMAGE_NAME):$(IMAGE_TAG)

publish-release:
	docker tag $(IMAGE_NAME):local $(IMAGE_NAME):$(IMAGE_TAG)
	docker tag $(IMAGE_NAME):local $(IMAGE_NAME):latest
	docker push $(IMAGE_NAME):$(IMAGE_TAG)
	docker push $(IMAGE_NAME):latest
