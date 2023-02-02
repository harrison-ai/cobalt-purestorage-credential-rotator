#!/bin/bash

set -euo pipefail

pip install -e .[dev]
pytest -sv
