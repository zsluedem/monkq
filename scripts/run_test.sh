#!/bin/bash

pytest tests --mypy
flake8 MonkTrader tests
isort --recursive --check-only MonkTrader tests