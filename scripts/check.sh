#!/bin/bash

set -eu

CI=${CI:-false}

if [[ ${CI,,} == "true" ]]
then
  uv run ruff check --select I --fix
	uv run ruff check
	uv run ruff format
else
  uv run ruff check --select I
	uv run ruff check
	uv run ruff format --check
fi
