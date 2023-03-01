#!/bin/bash

set -eu

CI=${CI:-false}

if [[ ${CI,,} == "true" ]]
then
  echo "checking formatting with black.."
  black --check .

  echo "checking isort.."
  isort . -c

  echo "checking pycln.."
  pycln --check .

else

  echo "formatting with black.."
  black .

  echo "running isort.."
  isort .

  echo "running pycln.."
  pycln .

fi
