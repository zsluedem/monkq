#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail

flake8 monkq tests
isort --recursive --check-only monkq tests
mypy monkq tests
