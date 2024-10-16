#!/usr/bin/env just --justfile

default: tests

build_dir := "dist"
python_src := "cff_from_621 tests"
version := `head -n1 cff_from_621/version.py | cut -d ' ' -f 3`

# applies black code style
black:
  python -m black {{python_src}}

# builds source distribution and wheel
build:
  rm {{build_dir}}/*
  python -m build

# runs integration tests
integration-tests:
  python -m pytest tests/test_integration.py

# checks code with black and flake8
lint:
  python -m flake8 --max-line-length=88 {{python_src}}

# validates type hints with mypy
mypy:
  python -m mypy {{python_src}}

# creates and publishes a release
release: tests
  git tag {{version}}
  git push upstream main:main
  git push upstream {{version}}

# runs all tests
tests: lint mypy integration-tests
