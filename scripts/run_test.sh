#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail

flake8 MonkTrader tests
isort --recursive --check-only MonkTrader tests
mypy MonkTrader tests
