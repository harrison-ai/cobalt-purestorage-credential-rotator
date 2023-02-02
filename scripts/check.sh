#!/bin/bash

set -eu

echo "formatting with black.."
black .

echo "running isort.."
isort .

echo "running pycln.."
pycln .