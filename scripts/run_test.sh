#!/bin/bash

flake8 MonkTrader tests
isort --recursive --check-only MonkTrader tests
pytest tests --mypy
