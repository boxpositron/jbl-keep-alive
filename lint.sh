#!/bin/bash

echo "Running linter"
poetry run python -m mypy app

echo "Running formatter"
poetry run python -m pycodestyle app
