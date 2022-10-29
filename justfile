#!/usr/bin/env just --justfile

default: tests

python_src := "cff_from_621 tests"

# applies black code style
black:
  python -m black {{python_src}}

# builds source distribution and wheel
build:
  python -m build

# runs integration tests
integration-tests:
  python -m pytest tests/test_integration.py

# checks code with black and flake8
lint:
  python -m flake8 --max-line-length=88 {{python_src}}

# runs all tests
tests: lint integration-tests
